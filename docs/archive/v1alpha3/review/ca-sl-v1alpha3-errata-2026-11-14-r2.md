# CA-SL vNext / v1alpha3 — Post-freeze Errata Review Round 2

**Date:** 2026-11-14  
**Classification:** Documentary errata and clarification of existing normative obligations (**A/B**, §45.1)  
**Language target:** **CA-SL v1alpha3 FROZEN**. Any substantive change to valid inputs, Evidence authority, authorization, Reconcile semantics or an already frozen diagnostic/result would require an explicit **v1alpha4** or a separately versioned interoperability contract.  
**Product/Owner conformance:** **NOT QUALIFIED**, exactly as in §45.2.  
**Normative source:** [Chinese CA-SL specification](../../../skill-language-spec.zh-CN.md).\
**Earlier errata:** [v1alpha3 errata round 1](ca-sl-v1alpha3-errata-2026-11-14.md).

This record follows an additional independent review. It identifies textual inconsistencies still present **after** the previous errata and distinguishes those from findings already corrected in main. It is not a substitute for the normative language or real Owner publications.

## Review disposition

| Finding | Classification | Remediation |
|---|---|---|
| H wrong case mapping / undefined E115/E116 | Earlier errata + additional A | The previous errata had already removed E115/E116 and fixed most mappings. In this round, remaining `CONTROL_FLOW_CYCLE→E60` and `CONTEXT_SCHEMA_MISMATCH→E95` were changed to **pending exact fixture**, not falsely cited; `UNKNOWN_FIELD→E35` restored because E35 contains a genuine unknown-field negative. |
| IndependentDomains and shared fact trust not enumerated under §34 | B: restate existing F.4/G.3.1 | Added §34.0.2 showing trusted input minimum, deployment/publisher authorization, immutable artifact bytes and digest, independent domain pairs, shared fact scope/value mapping. Missing/untrusted relation still produces `EVIDENCE_GUARANTEE_LINK_INVALID`. BuildRequest wire fields and digest framing remain separately versioned. |
| Inconsistent "incomparable" diagnosis | B: interpret existing §17.1.1/G.3 and E102 | **Invalid/missing/untrusted mapping** → Compiler `EVIDENCE_GUARANTEE_LINK_INVALID`; **valid mapping but statically provably impossible for any legal evidence combination** → Compiler `PREDICATE_EVIDENCE_UNSATISFIABLE`; **valid, statically satisfiable mapping but insufficient evidence on this execution** → Predicate UNKNOWN. No new trusted source or implicit independence. |
| §6.5 Reconcile Effect/Capability identity | A/B: terminology | Lists all three mutually exclusive Operation shapes. Reconcile invokes a separate READ callable, needs its own Capability, Scope, proof and budget; not a local no-Capability Script. Operation Result may expose only verified recovered business data, never the raw Reconcile receipt. |
| §12.7 "Reconcile Output Schema" | Already fixed in preceding errata | Confirmed text already links `reconcile-node.operation.output` exclusively to `mutation.reconcile.recoverableOutputSchema` and the committed recovered subobject. No new edit to authorization/output contract. |
| effectiveContext vs closed Host Schema | A: clarify two independent validations | §11.5 explicitly says Host Schema validates **Host portion**, Request Schema validates Request; their materialized logical view is not revalidated wholesale against the closed Host root. |
| §17.1 "omit parameter" | A | Refers to omitting a parameter's `evidence.requires` entry, **never** omitting its parameter/signature or arguments position. |
| §10.1 author sources | A | Explicitly names the three author roles: contract.yaml, procedure.yaml, predicates.yaml. |
| Duplicate EFFECT_MISMATCH in H | Already fixed in previous errata | `(Code, Phase)` is the unique diagnostic classification key; this round also adds a **normative clause locator column** for all 99 H rows. |
| §30 UDM accepted state and proof | B: educational contract assumption | The teaching Owner's SUCCEEDED/COMMITTED continuation now explicitly depends on **already published, linked and Runtime-verified** sufficient business data, Scope, Correlation, Freshness, Evidence and responsibility. COMMITTED alone proves submission, not business Goal. Real Owners without that proof must use separate Observation/Postcondition or safe stop. |

## Additional editorial and diagnostic clarifications

- §20.1 table now explicitly says **SUCCEEDED is the current Mutation stage edge**, not immediate successful Invocation termination.
- §24.1 specifies diagnostic precedence for **recognized** legacy Wait/Await (`UNSUPPORTED_WAIT`) and known v0.2 constructs (`UNSUPPORTED_V02_SYNTAX`) ahead of generic `UNKNOWN_FIELD`; malformed YAML is checked first. This is a narrowly scoped diagnostic disambiguation where the source was already rejected by all interpretations; it does **not** permit legacy compatibility or alter the outcome of an already specified Appendix E negative.
- §45.1 freezes a three-tier review process: **A editorial errata**, **B existing-rule disambiguation with evidence of unchanged accepted inputs/outcomes**, and **C versioned semantic/interop change**. If an apparent B changes a frozen E expected result or grants an unverified authority, reclassify as C and do not silently patch v1alpha3.
- The [E01–E114 trace index](../fixtures/ca-sl-v1alpha3-case-traceability.yaml) retains `ciFixture: null` until real executable tests run. E102 has separate C_STATIC / R_RUNTIME variants and was synchronized with the normative text.
- The [§22.1 route matrix mirror](../fixtures/ca-sl-v1alpha3-route-matrix.yaml) remains informative and subordinate to the spec.

## Trust-boundary and build digest interpretation

The source bytes and trusted digest for IndependentDomains and Shared Fact Binding are **part of the verified input closure** for the BuildRequest or equivalent trusted compile context. If the selected BuildRequest version has an aggregate digest, these verified inputs must be included in that committed closure. The CA-SL specification **does not invent a new top-level BuildRequest digest field or framing**. Implementations whose transport cannot supply/verify the mandatory abstract attributes must reject v1alpha3 interoperability rather than invent mappings. The `snapshotDigest` field remains mandatory in G.3.1; other signatures/immutable commitments may supplement but not replace it.

## Explicit non-claims and follow-up evidence

This PR is **not** an Owner contract publication, a Compiler, Studio or Runtime implementation, or a real 5GC exercise. Repository source hygiene, link review and static document parsing can establish only **document consistency**, not §45.2 qualified behavior. The exact per-diagnostic fixtures still marked `待补独立 Fixture` and Native/WASM/Studio parity, Owner proof exports, Runtime replay and the real 5GC 36-case migration remain open gates.

The language stays v1alpha3 only because these edits do **not** authorize additional data sources, change failure routing, modify the normalized Reconcile output visibility or invalidate an existing defined E01–E114 expected result. Any proof that one of those boundaries **did** change invalidates this errata classification and requires an explicit new language or interop version before implementing that change.
