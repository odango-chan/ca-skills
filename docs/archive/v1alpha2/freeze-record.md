# CA-SL vNext / v1alpha2 — Freeze Decision Record

**Date:** 2026-11-14  
**Decision:** LANGUAGE CONTRACT FROZEN; IMPLEMENTATION CONFORMANCE NOT QUALIFIED  
**Normative source:** [CA-SL 中文规范](../../skill-language-spec.zh-CN.md), including Appendix F\
**Change control:** Semantic changes require an explicitly new language or interoperability contract version; implementation deviations do not redefine v1alpha2.

## 1. Boundary of the freeze

This decision freezes author-facing Contract / Procedure / Predicates syntax; explicit argument binding; the four-stage DAG and route matrix; final Goal and global Precondition path coverage; conservative Schema assignability; typed callable identities, Capability membership and Scope; Evidence, correlation, freshness and record selection; Mutation reconciliation and resource responsibility; Script signatures and safety rules; versioned diagnostic and expected behavior fixtures.

Appendix F fixes the v1alpha2 interoperability properties of ToolCatalog, CapabilityContracts, Evidence descriptors and trusted linking inputs. The precise *transport* of those trusted inputs remains part of the separately versioned Compiler BuildRequest. Generated Compiler Artifacts and Runtime Trace wire encoding remain owned by their respective subsystems. The spec does not rename their fields, fabricate owner publications, or implicitly reintroduce a dependency package manager.

## 2. Freeze review matrix

| Earlier critical gap | Frozen resolution | Evidence level |
|---|---|---|
| Contract and Procedure ownership conflict | §10–11 and §28: Goal, Request, dependency and grants only in Contract | Document review |
| Procedure stage and route ambiguity | §12, §22.1: explicit four-stage order, auto-normal edge, terminal targets | Document + bounded graph review |
| Global Preconditions and final Goal coverage | §12.9, E17/E18/E50/E51/E100: path-sensitive proof and invalidation | Document + bounded graph review |
| Predicate parameter and Schema mismatches | §14, §29–30, F.5: ordered typed signature, conservative assignability | Document + arity review |
| Reconcile reading unavailable original success output | §12.7, §20, E10/E63: only guaranteed Reconcile output or new authoritative Observation | Document + bounded graph review |
| Mutation UNKNOWN vs unconditional retry | §20–22, E59/E60/E82/E85: safe original-call Reconcile or preserved unresolved stop | Document review |
| Evidence guarantees and independent records | §17, F.3, E19/E20/E32/E102 | Normative design; Runtime tests pending |
| Callable and deployment authorization | §9, F.1–F.2, E72/E81/E87/E88 | Normative design; Owner publication pending |
| Dependency/Owner provenance and snapshots | §34, F.4, E03–E05/E39/E43/E93/E103 | Normative design; BuildRequest integration pending |
| Static type and Script contract | §13–14, §32, F.5–F.6, E66–E75 | Normative design; Compiler/LSP tests pending |
| Asynchronous 5GC completion | §21: no Skill Wait; completion inside the three owning Operations | Normative target; Owner/E2E pending |

## 3. Performed checks and evidence limitations

- A lightweight independent control-flow scan of the **§30 teaching graph** counted **17 Nodes, 23 stages, and 81 expanded edges**. It traversed **16 successful outcome combinations**; no dangling route, missed Goal PASS, Predicate arity mismatch or missing previously produced output was detected by that scan.
- The **§12.1 reconcile teaching graph** counted **2 Nodes, 5 stages, 17 expanded edges and 2 successful combinations**; no graph/arity/output-availability error was detected.
- This review does **not** establish full Schema assignability, Owner publication, verified Evidence content, runtime reconciliation behavior or executable PDU session E2E. The scanner is a focused document consistency check, not CA-SL Compiler or a substitute for the normative Appendix E fixtures.
- GitHub's `source-hygiene` workflow is a source/document-level check only. Its result must be recorded against the **final PR head**; an earlier PASS does not certify a subsequently edited revision.
- The Appendix E fixture matrix defines required expected results. It is not an assertion that the present v0.2 Compiler/Studio/Runtime already support v1alpha2.

## 4. Cross-repository facts rechecked on 2026-11-14

- `odango-chan/ca-agent-demo` PRs [#198](https://github.com/odango-chan/ca-agent-demo/pull/198), [#199](https://github.com/odango-chan/ca-agent-demo/pull/199) and [#200](https://github.com/odango-chan/ca-agent-demo/pull/200) are **merged**. The old #24 PR description's Draft/OPEN snapshot is stale.
- `odango-chan/ca-provider-5gc` [#50](https://github.com/odango-chan/ca-provider-5gc/pull/50) is **open** and not merged; its Provider HTTP wire schema must not be confused with the separate Host-normalized `runtime_value()` projection.
- `odango-chan/ca-skill-compiler` [#4](https://github.com/odango-chan/ca-skill-compiler/pull/4) and [#6](https://github.com/odango-chan/ca-skill-compiler/pull/6) remain **open drafts**, not v1alpha2 semantic qualifications.
- The actual 5GC owner export bundle and Runtime Evidence guarantees still need independent Owner acceptance and release. The 36 conventional 5GC Cases remain behavior baselines, not proofs of a vNext executable migration.

## 5. Product compliance and non-claims

The Owner/Compiler/Studio/Native/WASM/Runtime/live-5GC gates of CA-SL §45.2 remain mandatory before anyone can claim *implementation conformity* or READY. **Language freeze is not a production implementation sign-off.** Do not silently rewrite v0.2 skills, duplicate external Schema inside ca-skills, downgrade safety checks, or treat a documentary source-hygiene PASS as runtime proof.

This record is non-normative and may track evolving implementation evidence without changing the frozen normative specification.
