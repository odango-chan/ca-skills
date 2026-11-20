# MAS Modify / Release acceptance matrix

**Current status: SOURCE_STATIC_ONLY.** The source Procedures and regression guards are authored here. No Owner, Host, Runtime or live 5GC E2E result is claimed. All runtime scenarios below remain NOT_RUN until the corresponding trusted contracts and private bindings exist.

| Scenario | Required setup / fault | Expected behavior | Current evidence |
| --- | --- | --- | --- |
| Successful Modify | m0, m2, m3, m4 and m5 settle for the same SUPI / PSI / generation; all final Predicates and Evidence pass. | Final Postcondition alone routes `SUCCEEDED`; m3 and m5 remain distinct Mutation occurrences. | Source graph and static regression test only |
| Successful Release | r1–r6 settle for the same SUPI / PSI / generation; r2 proves PFCP deletion; r3 proves its exact signal disposition; r4/r5/r6 prove their declared source outcomes. | Final Postcondition alone routes `SUCCEEDED`; Host ResourceMap tombstone remains a separate Host action. | Source graph and static regression test only |
| DENIED | Authorization / Scope is denied before dispatch. Repeat at the first operation and after one or more committed steps. | No Owner dispatch for the denied call. First-step denial may publish `FAILED`; after earlier commits publish `SAFE_STOPPED`. | Route contract authored; Runtime test NOT_RUN |
| OUTCOME_UNKNOWN | Drop the response, restart the Owner, omit a commit receipt, or lose the final callback after dispatch. | Never infer `NOT_COMMITTED`; no blind retry or new Release graph. Use only exact-original Host reconciliation when trusted; otherwise `SAFE_STOPPED`. | Route contract authored; Owner test NOT_RUN |
| Duplicate invocation | Replay the exact same original Invocation and idempotency identity. | Return the original result / receipt; no second Owner mutation. | Owner test NOT_RUN |
| Wrong generation | Deliver a receipt or callback carrying a generation different from the registered original occurrence. | Reject it; do not satisfy any Predicate or advance the graph. Preserve original responsibility. | Owner / Host test NOT_RUN |
| Late callback | Deliver a valid old callback after cancellation, terminal publication or a newer Run has started. | Attach only to the original retained occurrence; never resume or mutate the newer Run. | Owner / Host test NOT_RUN |
| Mixed UE | Reuse the same PSI across two SUPIs and cross-deliver a result / callback. | Exact SUPI + PSI + generation Scope prevents cross-UE satisfaction. | Owner / Host test NOT_RUN |
| Establishment s10 callback | Complete the N2 Setup Response for the existing Establishment `s10 OWNER_DEFERRED` occurrence. | Resume the original Establishment Operation in the same Run. Do not start Modify / Release or a new Run. | Host test NOT_RUN |
| Charging marker | Run Modify m2 or Release r1 against the pinned adapter. | Verify only `charging_ref="1"` / `"0"` local marker. Never claim a CHF reservation or deletion. | Pinned source inspection |
| Release r6 event | Run `SE.EMIT_EVENTS(ev="RELEASED")`. | Verify only the local MAS event record. Never claim 3GPP SM Context Status Notify. | Pinned source inspection |
| OES r7 | Inspect `COMPENSATE_RELEASE` and `compensate_then_replan_once`. | r7 remains excluded; no automatic compensation / replan / retry is authored. | Pinned plan inspection |

The committed Python regression suite checks source graph shape, source pinning, route safety, entry variants, non-claims and the presence of these scenario definitions. It is not a simulation of Owner receipts or Host concurrency, and it must not be reported as an E2E pass.
