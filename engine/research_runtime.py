"""Deterministic retrieval loop, evidence intake, entity frontier and auditable completion."""
from __future__ import annotations
from dataclasses import asdict, replace
import hashlib
from math import isfinite
import re
from urllib.parse import urlparse
from agent_os import Node, NodeStatus
from research_config import ResearchConfig
from research_contracts import AtomicClaim, EpistemicStatus, get_gate
from research_executor import MissingResearchExecutor, ResearchBackendUnavailable
from research_bridge import ResearchBridge
from research_planner import questions_for, generic_entity_discovery_questions
from economic_graph import EconomicGraph, EvidenceRef

class ResearchRuntime:
    def __init__(self, graph, ctx):
        self.graph, self.ctx = graph, ctx
        self.config = ctx.setdefault('research_config', ResearchConfig())
        self.bridge = ctx.setdefault('research_bridge', ResearchBridge())
        self.memory = self.bridge.memory
        self.economy = ctx.setdefault('economic_graph', EconomicGraph())
        self.trace = ctx.setdefault('research_trace', [])
        self.aliases = ctx.setdefault('entity_aliases', {})
        self.executor = ctx.get('research_executor') or MissingResearchExecutor()

    def checkpoint(self, event, payload=None):
        sink = self.ctx.get('run_writer')
        if sink: sink.checkpoint(self, event, payload)
        progress = self.ctx.get('progress')
        if progress: progress(event, payload or {})

    def resolve_identity(self, node):
        """Require independent quoted domain attribution plus a self-identification page.

        Domain strings are parsed from accepted quotes, never from model metadata or result rank.
        Ambiguous multi-domain matches remain unresolved.
        """
        v = node.value if isinstance(node.value, dict) else {}
        name = v.get('canonical_name', '')
        claims = [c for c in self.memory.for_subject(node.id)
                  if c.field == 'identity' and c.status == EpistemicStatus.FACT
                  and name.casefold() in c.quote_or_excerpt.casefold()]
        matches = {}
        for c in claims:
            for source in c.sources:
                host = (urlparse(source.url).hostname or '').removeprefix('www.')
                for other in claims:
                    if other.claim_id == c.claim_id: continue
                    for ref in other.sources:
                        refhost = (urlparse(ref.url).hostname or '').removeprefix('www.')
                        if refhost == host or refhost.endswith('.'+host) or host.endswith('.'+refhost): continue
                        if ref.tier > 3: continue
                        domains = re.findall(r'(?<![\w.-])(?:https?://)?(?:www\.)?([a-z0-9-]+(?:\.[a-z0-9-]+)+)', other.quote_or_excerpt.lower())
                        if host in domains:
                            matches.setdefault(host,set()).update((c.claim_id,other.claim_id))
        if len(matches)==1:
            host, ids = next(iter(matches.items()))
            v.update(official_domain=host, canonical_url='https://'+host,
                     identity_status='CORROBORATED', identity_evidence_claim_ids=sorted(ids))
        else:
            v.setdefault('identity_status','UNVERIFIED' if not matches else 'AMBIGUOUS')
        node.value = v

    def gate(self, node):
        v = node.value if isinstance(node.value, dict) else {}
        return get_gate(node.completion_gate or node.node_type).evaluate(
            self.memory.for_subject(node.id), node.critical_unknown_fields,
            searches=[s for s in self.memory.searches if s['node'] == node.id],
            profile=v.get('profile'), config=self.config, supporting_claims=self.support_closure(node.id))

    def support_closure(self, subject):
        pending = [i for c in self.memory.for_subject(subject) for i in c.supporting_claim_ids]
        found = {}
        while pending:
            i = pending.pop()
            if i in found or i not in self.memory.claims:continue
            found[i] = self.memory.claims[i]
            pending.extend(found[i].supporting_claim_ids)
        return list(found.values())

    def execute(self, node, questions, executor=None):
        executor = executor or self.executor
        entities, records = [], []
        for q in questions[:self.config.max_queries_per_round]:
            limit = self.ctx.get('active_query_limit', self.config.max_queries)
            if len(self.memory.searches) >= limit:
                self.ctx.setdefault('budget_exhausted',set()).add('max_queries')
                break
            v = node.value if isinstance(node.value,dict) else {}
            review_subject = q.question_id.removeprefix('adversarial:')
            context = (self.memory.for_subject(review_subject) + self.support_closure(review_subject)
                       if review_subject in self.graph.nodes else list(self.memory.claims.values())[-60:]) if node.node_type == 'red_team' else (
                self.memory.for_subject(node.id) + self.support_closure(node.id) +
                self.memory.for_subject(v.get('company_id','')))
            q = replace(q,subject_id=node.id,question_id=node.id+":"+q.question_id,
                        context_claims=tuple(context), preferred_domains=((v['official_domain'],)
                        if v.get('identity_status') == 'CORROBORATED' else q.preferred_domains))
            record = dict(agent=q.agent, node=node.id, missing_field=list(q.target_fields),
                target_fields=list(q.target_fields), question=q.question_id, query=q.query,
                negative_query=q.negative_query, search_results_considered=[], sources_opened=[],
                claims_added=[], claims_rejected=[], contradictions_added=[], entities_discovered=[],
                children_spawned=[], completion_gate_before=asdict(self.gate(node)) if node.completion_gate else {},
                completion_gate_after={}, status='STARTED')
            # Record first; exceptions and interruption leave an auditable attempted action.
            self.trace.append(record)
            records.append(record)
            self.checkpoint('SEARCH', record)
            try:
                results = executor.search(q)
                record['search_results_considered'] = [asdict(r) for r in results]
                record['status'] = 'SEARCHED'
                for result in results[:self.config.max_results_per_query]:
                    try:
                        doc = executor.open_source(result)
                        if doc.source.url != result.url:
                            raise ValueError('retrieved URL differs; adapter must return a canonical SearchResult')
                        self.memory.remember_source(doc)
                        record['sources_opened'].append(doc.source_id)
                        self.checkpoint('OPEN', {'node':node.id,'url':doc.source.url})
                        proposed = executor.extract_claims(doc, [q])
                        accepted = []
                        for c in proposed:
                            try:
                                if c.subject_id != node.id:
                                    raise ValueError('claim subject differs from current research node')
                                if c.field not in q.target_fields and c.field != 'counterevidence':
                                    raise ValueError('claim does not answer this research question')
                                if self.memory.accept(c, doc):
                                    record['claims_added'].append(c.claim_id)
                                accepted.append(self.memory.claims[c.claim_id])
                                self.checkpoint('CLAIM', {'node':node.id,'claim_id':c.claim_id})
                                record['contradictions_added'].extend(c.contradictory_claim_ids)
                            except (ValueError, AttributeError, TypeError) as exc:
                                record['claims_rejected'].append({'id': getattr(c,'claim_id',None), 'reason':str(exc)})
                        if node.node_type == 'company': self.resolve_identity(node)
                        if any(c.status in (EpistemicStatus.FACT,EpistemicStatus.EVIDENCE) for c in accepted):
                            record.setdefault('useful_sources',[]).append(doc.source_id)
                        for reason in getattr(executor,'last_extraction_notes',[]):
                            record['claims_rejected'].append({'id':None,'reason':reason})
                        if hasattr(executor, 'discover_entities'):
                            new = executor.discover_entities(doc, accepted, {'node_id':node.id,
                                'objective':self.ctx.get('objective',node.question), 'node_type':node.node_type})
                            entities.extend(new)
                            record['entities_discovered'].extend(asdict(e) for e in new)
                    except Exception as exc:
                        record.setdefault('source_errors', []).append({'url':result.url, 'error':str(exc)})
                # Failed retrieval/extraction is not a completed negative search.
                if not record['sources_opened'] or record.get('source_errors'):
                    record['status'] = 'SOURCE_ACCESS_FAILED'
                elif not record.get('useful_sources'):
                    record['status'] = 'NO_RELEVANT_EVIDENCE'
            except ResearchBackendUnavailable:
                record['status'] = 'RESEARCH_BACKEND_REQUIRED'
            except Exception as exc:
                record['status'] = 'RESEARCH_BACKEND_ERROR'
                record['error'] = str(exc)
            self.memory.record_search(record)
            if node.completion_gate:
                record['completion_gate_after'] = asdict(self.gate(node))
            self.checkpoint('QUERY_COMPLETE',record)
            if record['status'] in ('RESEARCH_BACKEND_REQUIRED', 'RESEARCH_BACKEND_ERROR'):
                break
        return entities, records

    @staticmethod
    def identity_keys(ent):
        # Exact normalized names plus canonical URLs; never collapse all business units by domain.
        name = re.sub(r'[^a-z0-9]+', ' ', ent.canonical_name.casefold()).strip()
        keys = [(ent.entity_type, 'name:' + name)]
        if ent.canonical_url:
            u = urlparse(ent.canonical_url)
            keys.append((ent.entity_type, 'url:' + (u.hostname or '').removeprefix('www.') + u.path.rstrip('/')))
        return keys

    def spawn(self, parent, entities):
        spawned, rejected = [], []
        for e in entities:
            why = None
            refs = [self.memory.claims.get(i) for i in e.evidence_claim_ids]
            if e.profile not in (None,'general','developer','industrial_rd','talent'):
                rejected.append({'entity':e.canonical_name,'reason':'UNKNOWN_PROFILE'})
                continue
            if not e.canonical_name.strip() or not refs or any(c is None for c in refs):
                why = 'MISSING_ACCEPTED_DISCOVERY_EVIDENCE'
            elif not any(c.status == EpistemicStatus.FACT and c.strongest_tier <= 3 for c in refs):
                why = 'WEAK_SOURCE'
            elif not e.relevance.strip() or not isfinite(e.voi) or e.voi < self.config.min_entity_voi:
                why = 'LOW_RELEVANCE_OR_VOI'
            elif parent.depth >= self.config.max_dependency_hops:
                why = 'MAX_DEPENDENCY_HOPS'
            keys = self.identity_keys(e)
            existing = next((self.aliases[k] for k in keys if k in self.aliases), None)
            if not why and existing:
                for k in keys:self.aliases[k] = existing
                n = self.graph.get(existing)
                ids = n.value.setdefault('discovery_claim_ids', [])
                ids.extend(i for i in e.evidence_claim_ids if i not in ids)
                why = 'DUPLICATE'
            if not why and not existing and e.entity_type == 'company' and sum(n.node_type=='company' for n in self.graph.all()) >= self.config.max_companies:
                why = 'COMPANY_BUDGET_EXHAUSTED'
                self.ctx.setdefault('budget_exhausted',set()).add('max_companies')
            if not why and len(self.graph.nodes) >= self.config.max_nodes:
                why = 'NODE_BUDGET_EXHAUSTED'
            if why:
                rejected.append({'entity':e.canonical_name, 'reason':why})
                continue
            nid = e.entity_type + ':' + hashlib.sha256(repr(keys[0]).encode()).hexdigest()[:16]
            for k in keys:self.aliases[k] = nid
            from research_contracts import GATES
            gate = e.entity_type if e.entity_type in GATES else None
            n = Node(nid, f'Research {e.entity_type}: {e.canonical_name}',
                resolver='dynamic_company_research' if e.entity_type == 'company' else 'dynamic_entity_research',
                node_type=e.entity_type, completion_gate=gate, depth=parent.depth+1, voi=4.5 if self.ctx.get('live_mode') and e.entity_type=='company' else e.voi,
                auto_rollup=False, value={'profile':e.profile,'canonical_name':e.canonical_name,'canonical_url':e.canonical_url,
                'discovery_claim_ids':list(e.evidence_claim_ids),'event_connection':e.relevance})
            if e.entity_type in ('theme','event_concept'):
                n.value['epistemic_status'] = 'HYPOTHESIS'
            self.graph.add(n)
            econ_refs = [EvidenceRef(s.url,s.title,s.source_type or 'unknown',c.statement)
                         for c in refs for s in c.sources]
            self.economy.add_node(e.entity_type,e.canonical_name,node_id=nid,evidence=econ_refs)
            if parent.id in self.economy.nodes and e.relationship:
                from economic_graph import REQUIRED_EDGE_TYPES
                if e.relationship in REQUIRED_EDGE_TYPES:
                    self.economy.add_edge(parent.id,nid,e.relationship,evidence=econ_refs)
            spawned.append(nid)
            self.checkpoint('ENTITY', {'node':nid,'name':e.canonical_name})
        return spawned, rejected

    def research(self, node, executor=None):
        if not node.completion_gate:
            return 'CONTRACT_REQUIRED'
        self.checkpoint('RESEARCH',{'node':node.id,'name':node.question})
        start_queries = len(self.memory.searches)
        for round_number in range(self.config.max_rounds):
            before = self.gate(node)
            if before.complete:
                return 'EVIDENCE_COMPLETE'
            fields = before.missing + before.weak + before.primary_validation
            fields = [f.removeprefix('search:').removeprefix('negative_search:').removeprefix('contradiction:') for f in fields
                      if f not in ('primary_sources','independent_sources')]
            if node.node_type=='company' and self.ctx.get('live_mode'):
                fields += ['existing_programs','research_blind_spot','uncertainty','parallelizable',
                           'prototypeable_in_event','evaluable','failure_information_valuable',
                           'internal_substitute_researched','ip_understood','student_fit','needs_deep_domain']
            if not fields:
                fields = [r.field for r in get_gate(node.completion_gate).requirements]
            # Rotate field blocks so budget caps cannot starve the last requirements forever.
            from dataclasses import replace
            # VOI heuristic: prioritize disputed/unknown fields and fields with weaker current evidence.
            priorities = dict(self.config.field_priorities)
            for f in fields:
                cs = [c for c in self.memory.for_subject(node.id) if c.field == f]
                uncertainty = 1 if not cs or any(c.contradictory_claim_ids for c in cs) else 1-max(c.confidence for c in cs)
                priorities.setdefault(f, uncertainty)
            planner_config = replace(self.config, field_priorities=priorities)
            queries = questions_for((node.value or {}).get('canonical_name',node.question), fields, node.node_type, round_number, planner_config,
                                    tuple(s['query'] for s in self.memory.searches if s['node']==node.id),
                                    self.memory.for_subject(node.id))
            if not self.ctx.get('live_mode') and len(queries) > self.config.max_queries_per_round:
                offset = (round_number * self.config.max_queries_per_round) % len(queries)
                queries = queries[offset:] + queries[:offset]
            if self.ctx.get('live_mode'):
                allocation = self.ctx.get('company_query_budget',self.config.max_queries) if node.node_type=='company' else 6
                remaining = allocation-(len(self.memory.searches)-start_queries)
                batch = min(self.config.max_queries_per_round, max(3,((allocation + self.config.max_rounds*3-1)//(self.config.max_rounds*3))*3))
                offset = (round_number*batch)%max(1,len(queries))
                queries = (queries[offset:]+queries[:offset])[:max(0,min(remaining,batch))]
            entities, records = self.execute(node, queries, executor)
            spawned, stops = self.spawn(node, entities)
            if records:
                records[-1]['children_spawned'] = spawned
                records[-1]['entity_stop_reasons'] = stops
            v = node.value if isinstance(node.value, dict) else {}
            v.update(supporting_claims=self.support_closure(node.id), research_config=asdict(self.config), claims=self.memory.for_subject(node.id),
                searches=[s for s in self.memory.searches if s['node']==node.id],
                gate=asdict(self.gate(node)))
            node.value = v
            self.checkpoint('NODE', {'node':node.id,'gate':v['gate']})
            if not records: break
            if records and records[-1]['status'].startswith('RESEARCH_BACKEND_'):
                return records[-1]['status']
        if not self.gate(node).complete:
            self.ctx.setdefault('budget_exhausted',set()).add('research_round_or_node_allocation')
        return 'EVIDENCE_COMPLETE' if self.gate(node).complete else 'ROUND_BUDGET_EXHAUSTED'

    def discover(self, node):
        quiet = 0
        for round_number in range(self.config.max_rounds):
            entities, records = self.execute(node, generic_entity_discovery_questions(node.question,
                round_number, [n.name for n in self.economy.nodes.values()]))
            spawned, stops = self.spawn(node, entities)
            if records:
                records[-1]['children_spawned'] = spawned
                records[-1]['entity_stop_reasons'] = stops
            if any(s['reason'] in ('NODE_BUDGET_EXHAUSTED','COMPANY_BUDGET_EXHAUSTED','MAX_DEPENDENCY_HOPS') for s in stops):
                return 'DISCOVERY_BUDGET_EXHAUSTED'
            if not records or any(r['status'] != 'SEARCHED' for r in records):
                return records[-1]['status'] if records else 'RESEARCH_BACKEND_REQUIRED'
            # No extraction capability or no opened evidence is absence of research, not saturation.
            if not hasattr(self.executor,'discover_entities') or not any(c.status == EpistemicStatus.FACT and c.strongest_tier <= 3 for c in self.memory.for_subject(node.id)):
                return 'DISCOVERY_EVIDENCE_REQUIRED'
            fraction = len(spawned) / max(1, len(entities))
            quiet = quiet + 1 if fraction <= self.config.max_new_entity_fraction else 0
            if quiet >= self.config.saturation_rounds:
                node.value = {'claims':self.memory.for_subject(node.id), 'saturation_rounds':quiet,
                              'discovered_node_ids':list(self.economy.nodes)}
                return 'SATURATED'
        self.ctx.setdefault('budget_exhausted',set()).add('discovery_rounds')
        return 'DISCOVERY_ROUND_BUDGET_EXHAUSTED'

    def map_opportunities(self, company):
        mapper = self.ctx.get('opportunity_mapper')
        if mapper is None:
            return []
        from research_opportunities import ResearchOpportunity
        try:
            proposed = mapper.map_opportunities(company_id=company.id,
                claims=self.memory.for_subject(company.id))
        except Exception as exc:
            self.trace.append({'agent':'opportunity_mapper','node':company.id,'status':'REJECTED','error':str(exc)})
            return []
        for error in getattr(mapper,'rejections',[]):
            self.trace.append({'agent':'opportunity_mapper','node':company.id,'status':'REJECTED','error':error})
        out = []
        for spec in proposed:
            if not isinstance(spec,ResearchOpportunity):
                self.trace.append({'agent':'opportunity_mapper','node':company.id,'status':'REJECTED',
                                   'reason':'typed ResearchOpportunity required'})
                continue
            errors = spec.validate(self.memory,self.config)
            if spec.company_id != company.id:errors.append('company_id_mismatch')
            if len(self.graph.nodes) >= self.config.max_nodes or company.depth >= self.config.max_dependency_hops:
                errors.append('opportunity_budget_exhausted')
            if errors:
                self.trace.append({'agent':'opportunity_mapper','node':company.id,'status':'REJECTED','errors':errors})
                continue
            nid = spec.kind + ':' + hashlib.sha256((company.id+spec.question).encode()).hexdigest()[:16]
            self.graph.add(Node(nid,spec.question,resolver='dynamic_entity_research',node_type=spec.kind,
                completion_gate=spec.kind,depth=company.depth+1,auto_rollup=False,
                value={'opportunity':spec,'company_id':company.id,'epistemic_status':'HYPOTHESIS'}))
            # Actual legacy kernel instances, shared across plans so burden cannot be reset per sponsor.
            from capture import ConsentLedger
            from burden_budget import BurdenBudget
            ledger = self.ctx.setdefault('consent_ledger',ConsentLedger())
            burden = self.ctx.setdefault('burden_budget',BurdenBudget(self.config.participant_burden_cap_sec))
            self.ctx.setdefault('live_opportunity_tools',{})[nid] = spec.live_tools(self.config,ledger,burden)
            out.append(nid)
            self.trace.append({'agent':'opportunity_mapper','node':company.id,'status':'PROPOSED',
                               'children_spawned':[nid], 'evidence_claim_ids':list(spec.evidence_claim_ids)})
        return out
