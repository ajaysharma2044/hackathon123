# State machine

Successful closed: **RESOLVED only**.
Closed but unresolved: **KILLED, BLOCKED**. Neither can satisfy a dependency.
Open: UNRESEARCHED, RESEARCHING, PARTIAL, CONTRADICTED, EVIDENCE_COMPLETE, SYNTHESIS_READY,
PRIMARY_VALIDATION_REQUIRED, RESEARCH_BACKEND_REQUIRED, CONTRACT_REQUIRED, RESEARCH_EXHAUSTED.
The latter three are non-dispatchable until an explicit resume. UNKNOWN/RESOLVING/NEEDS_RESEARCH/DECOMPOSED and PRIMARY/QUOTE remain
backward-compatible aliases with their new semantics.

A dispatch starts RESEARCHING. Exhausted round budgets become RESEARCH_EXHAUSTED; explicit critical buyer questions
stay PRIMARY_VALIDATION_REQUIRED; conflicting claims stay CONTRADICTED. A passing evidence contract
permits resolution. EVIDENCE_COMPLETE and SYNTHESIS_READY are representable intermediate states,
not dependency success; the current synchronous governor validates and commits resolution in one dispatch.

Both Evidence and parent rollup must pass required dependencies/children and the parent's contract.
Evidence.status is honored. Defer(RESOLVED) cannot promote a node. Node.resolve also checks a declared
contract. Typed research nodes receive gates automatically; the governor additionally checks their
claims against accepted opened-source memory. Historical untyped computational nodes can still
resolve deterministic results; they are not used for production factual research.

NodeGraph.add does not overwrite an existing ID. Circular dependencies have no ready nodes and
terminate without success. Related-entity links do not become cyclic required-child dependencies.
Independent red-team counterevidence reopens affected owners and invalidates downstream decisions.
Contradictions are not automatically adjudicated away: challenged questions remain open until the
research design/claim scope is explicitly revised. Governor.resume is an explicit bounded retry;
it never retries external actions or deletes contradictory evidence.

The concurrent branch's attempt_count/max_attempts/can_retry API is retained. The granular research
loop owns per-dispatch query rounds; deferrals pause outer retries to avoid multiplying those budgets
or repeatedly calling an unavailable provider. Explicit resume re-arms bounded attempts.
