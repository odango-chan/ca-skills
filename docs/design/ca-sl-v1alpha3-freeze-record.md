# CA-SL vNext / API v1alpha3 — Language Freeze Decision

**Decision date:** 2026-11-14  
**Normative source:** [CA-SL 中文规范](../skill-language-spec.zh-CN.md), especially §§10–24 and Appendices F, G, H  
**Decision:** FROZEN LANGUAGE CONTRACT; IMPLEMENTATION / OWNER CONFORMANCE **NOT QUALIFIED**  
**Post-freeze documentary errata:** [Round 1](ca-sl-v1alpha3-errata-2026-11-14.md), [Round 2](ca-sl-v1alpha3-errata-2026-11-14-r2.md), , [diagnostic/PSI trace clarification](ca-sl-v1alpha3-diagnostic-trace-errata.md), and [interop clarification](ca-sl-v1alpha3-interop-clarifications-2026-11-14.md) — no language version change; product/Owner conformance still pending.
**Prior version:** [v1alpha2 freeze record](ca-sl-v1alpha2-freeze-record.md) is historical. This release does **not** stealth-edit v1alpha2 safety semantics.

## 1. Why v1alpha3 was necessary

The follow-up review of PR #24 accepted the model conditionally but found ten closure gaps. Some were editorial; others affected externally observable security and interoperation semantics (Reconcile Effect, state and proof linkage, Evidence independence, typed Schema/CEL behavior and resource responsibility). All were closed under a **new explicit v1alpha3 version**; they must not be backported as meaning-changing v1alpha2 errata.

| Review finding | Normative closure | Key negative or positive cases |
|---|---|---|
| Incomplete grammar / identifiers / PredicateSet | G.1 provides exact abstract object grammar, ASCII IDs, qualified Schema URI and path rules | E105 |
| Reconcile callable Effect, input, proof, output, capability membership | G.2, G.2.1–G.2.2: READ-only independent callable, explicit original invocation, receiptSchema, proofPath, immutable commitState and separate conditional recovered output | E60, E78, E86, E107–E109 |
| Evidence independence grammar and failure priority | G.1, G.3, G.3.1; requires membership, source domain and trusted independent-domain relation; identical Ref is not independent identity | E32, E102, E106 |
| JSON Schema whitelist and CEL mapping | G.4–G.4.1: closed Draft 2020-12 subset, exact dialect, static nullable/presence, no unsupported composition, numeric precision | E09, E67–E75, E110–E111 |
| Scattered/ambiguous diagnostics | Appendix H canonical layer-index, §24.1–24.2 updated; Runtime diagnostics separated from phase outcomes | E70, E87–E88, E105–E114 |
| Pending resource record determines SAFE_STOPPED | G.5 Normative minimum resource responsibility model with authenticated source and tri-state disposition | E23, E96, E112 |
| Host/Request context split | G.6 explicitly composes logical effectiveContext without allOf or implicit Owner fallback | E25, E95, E113 |
| Long workflow old Evidence invalidation | G.8 explicit near-terminal Observation/Goal PASS refresh; forbids implicit producer replacement | E30, E40, E100 |
| Skill identity and secure file paths | G.1, G.7, exact POSIX package name/path, no traversal or casefold collisions | E105, E114 |
| Ambiguous Stage Outcome vs Invocation status | G.8 and §22.1, explicit route-key/status-value distinction | E17/E18, E70 |

## 2. Additional corrections discovered during closure

- Reconcile's **raw Owner output envelope** cannot be equated with its recoverable business result. A SUCCEEDED query proving NOT_COMMITTED can validly have no recovered resource. G.2 freezes an optional recovered output path, a separate Owner outputSchema and a mandatory recoverableOutputSchema+path pair when recovery is offered.
- A proofSchema without a publication path is not executable: Mutation and Reconcile now publish trusted receiptSchema, explicit proof paths, a fixed original invocation / COMMITTED or NOT_COMMITTED proof shape, and failureClassPath + per-class proofPath for deterministic failure result mapping.
- An Evidence independence source domain comparison requires trusted sourceIdentity; different domains are independent only if a trusted deployment supplies their explicit unordered IndependentDomains relation. Same-fact cross-Owner matching requires approved factIdentity / Scope mapping.
- Added IDENTIFIER_INVALID, QUALIFIED_REFERENCE_INVALID, PACKAGE_PATH_INVALID, CEL_INVALID, OWNER_OUTCOME_UNDECLARED, and separately indexed EVIDENCE_STALE / EVIDENCE_CONFLICT. OUTCOME_UNKNOWN remains a **stage outcome**, never a diagnostic.

## 3. Performed document-level checks

- §30 full teaching DAG and §12.1 reconcile teaching DAG were independently scanned in the earlier PR review: 17 Nodes / 23 stages / 81 edges, and 2 Nodes / 5 stages / 17 edges respectively. They had no detected dangling route, absent final Goal PASS, Predicate arity mismatch or unavailable prior output in the limited scan. These graphs were not rewritten by this v1alpha3 closure.
- The updated spec was checked for balanced Markdown fenced blocks, full diagnostic-code index coverage against the Compiler and Runtime tables, and explicit Draft 2020-12 declarations in the Schema examples.
- GitHub's source-hygiene check provides repository-source validation; its final result belongs to the final PR head and should be linked in the PR body.
- No v1alpha3 Compiler Native/WASM, Studio, Host/Runtime, Owner contract or live 5GC qualification is claimed by those checks. Appendix E01–E114 is a normative expected-result test matrix, **not** an existing automated test run.

## 4. Separate implementation / deployment acceptance

CA-SL §45.2 remains binding before any implementation can claim conformance or production readiness:

1. Real trusted ToolCatalog, Evidence and Scope exports for Owner contracts.
2. BuildRequest version transport of trusted Package/Owner identity, deployment authorization, scope mappings and receipt proof schemas.
3. Executable Compiler fixtures E01–E114, deterministic diagnostics and Script/CEL/Schema validation.
4. Native/WASM/Skill Studio parity; Runtime replay, proof/freshness, safe stop, budget and multi-UE concurrency.
5. Full conventional 5GC migration with the 36 behavior cases; MAS remains design-only; Provider GetSmData wire response and Host runtime_value() projection remain distinct contract boundaries.
6. Independent Compiler Artifact and Runtime Trace versioned protocol approval.

The current v0.2 executable Skill is not automatically v1alpha3. Real Owner publications or toolchain implementations not supporting this target must **fail closed** rather than silently weaken identity, guarantee, scope, or failure rules.

**Change control:** semantic or wire-format changes after this language freeze require an explicit new language/interop version. Clarifying typographical errata may not alter E01–E114 expected behavior. This record is non-normative; the canonical Chinese spec is the sole language authority.
