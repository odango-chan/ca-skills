# MAS Modify / Release acceptance matrix

**Current status: SOURCE_STATIC_ONLY.** The v1alpha5 Procedures and source mapping are authored. No trusted MAS Owner publication, Host / Runtime acceptance or live 5GC E2E result is claimed.

> Scope note: this matrix is the CA-SL authoring/qualification view. The real
> OpenAMSM 5GC E2E results (UE Modify/Release, PFCP reconcile, restart) live in
> `docs/scheme-c-3gpp-traceability.md` and are a **separate** verdict layer. A
> 5GC behaviour PASS is not a CA-SL Runtime PASS, and vice versa.

## Static source acceptance

| Check | Expected result | Current evidence |
| --- | --- | --- |
| CA-SL version | Both packages use connectionagent.io/v1alpha5 syntax only | Procedure / Contract / Predicate sources |
| Modify graph | m0 -> m3 -> m4 -> m5 -> final Postcondition | Static regression test |
| Release graph | r2 -> r3 -> r4 -> r5 -> r6 -> final Postcondition | Static regression test |
| Exact OES output shape | r3, r4 and r6 have empty output objects; no synthetic fields | Pinned plan and source mapping |
| Profile separation | m5 uses the dedicated v0.3.0 UPN.MODIFY_QOS_FLOWS contract; it does not reuse the v0.2.0 n3_synced profile | Candidate source-map comparison |
| Profile separation | m3, m4, r3 and r6 use distinct typed callable profiles | Static regression test |
| QoS delta target | m5 carries one closed QFI/5QI/GBR/MBR target; the Postcondition compares all six result fields with the request, plus the APPLIED dispatch state | Static + Predicate positive/negative tests |
| Completion scope | Goal = PFCP_APPLIED + N1N2_DISPATCHED on the exact target; APPLIED is not RAN confirmation; TARGET_STATE_VERIFIED requires an independent read | Documentation + E2E evidence |
| Optional steps | m2 and r1 are omitted because no applicability predicate exists | Pinned OES plan |
| Compensation | r7 remains excluded; no compensation / replan / retry is authored | Pinned OES plan and static test |
| Trigger values | Release uses numeric values 1..7 and Host-derived entryKind consistency | xact.h source pin and Predicate test |
| Release source defect | start_inputs is empty while r2/r3 reference trigger; linking remains blocked | Pinned OES plan |
| Owner publication | Missing trusted MAS ToolCatalog / CapabilityContracts / receipts remain fail-closed | Compiler v2.0.2 CI gate |
| Synthetic contract closure | Establishment, Modify and Release each pass Check / Inspect / Build against the v0.3.0 synthetic Owner fixture | Source Hygiene CI PASS; all reports remain NOT_QUALIFIED |

## Qualification scenario matrix

| Scenario | Required behavior | Status |
| --- | --- | --- |
| Modify success | m0/m3/m4/m5 settle for the same SUPI / PSI / generation; all final Predicates and Evidence pass | Development E2E PASS on the isolated D5 stack (ca-agent-demo evidence); Production NOT_RUN |
| QoS delta target state | Independent /pdu-info equals the requested QFI/5QI/GBR/MBR and the PFCP QER carries the same bitrates | Development E2E PASS (isolated stack) |
| UE-initiated Modify | Host authenticates a new UE UpdateSMContext business action | Host test NOT_RUN |
| AMF-initiated Modify | Host authenticates a new AMF business action, not a continuation callback | Host test NOT_RUN |
| Network-triggered Modify | Only a trusted internal Owner event may select this entry variant | Host test NOT_RUN |
| Release success | r2/r3/r4/r5/r6 settle for the same SUPI / PSI / generation | Runtime NOT_RUN |
| UE-initiated Release | trigger=2; matching release signaling completes | Owner / Host test NOT_RUN |
| AMF-initiated Release | trigger=6 or 7; source-defined no-N1/N2 branch completes | Owner / Host test NOT_RUN |
| Network-triggered Release | trigger=1, 3, 4 or 5; source-specific signaling behavior is respected | Owner / Host test NOT_RUN |
| PFCP deletion | r2 returns released=1 only after the matching PFCP delete completion | Owner test NOT_RUN |
| SSM Release callback | r3 completes only on no-signal proof or matching AMF release confirmation | Owner / Host test NOT_RUN |
| PCF deletion | r4 evidence distinguishes DELETED from NOT_PRESENT | Owner test NOT_RUN |
| Release event | r6 proves only the local in-memory marker; no 3GPP Status Notify claim | Source inspection only |
| DENIED | No Owner dispatch; first-step denial may end FAILED, later denial SAFE_STOPPED | Runtime NOT_RUN |
| OUTCOME_UNKNOWN | SAFE_STOPPED; no blind retry, compensation or new Run | Owner / Runtime NOT_RUN |
| Duplicate invocation | Exact replay returns original result / receipt without a second mutation | Owner test NOT_RUN |
| Wrong generation | Reject receipt / callback with a different private generation | Owner / Host test NOT_RUN |
| Late callback | Attach only to original pending occurrence; never resume a newer Run | Owner / Host test NOT_RUN |
| Mixed UE | Same PSI across two SUPIs cannot cross-satisfy Scope or Evidence | Owner / Host test NOT_RUN |
| Establishment s10 callback | Resume the original Establishment Run; do not start Modify / Release | Host test NOT_RUN |
| ResourceMap tombstone | Host performs it only after exact Release settlement; it is not a Skill output | Host test NOT_RUN |

## Verification boundary

The repository regression test checks the source graph, typed profile references, trigger mapping, safe routes, optional-step exclusions, source pins and non-claims. It does not simulate Owner receipts, callback races, generation isolation or a live network.

The CI workflow uses the released Compiler v2.0.2 to reject YAML / v1alpha5 grammar errors while requiring the expected missing-Owner dependency diagnostic. It also fetches the ca-client-tools v0.3.0 candidate at pinned commit `ff1dc3ef938ccd9594ce55d72986a67622c00921`, materializes a synthetic Owner / Capability / Evidence fixture and runs Check, Inspect and Build for all three MAS Skills. All three synthetic Builds pass; this proves only static link-shape compatibility with synthetic data and does not produce trusted Owner artifacts or qualify the real Provider.

All Owner publication, Host binding, Runtime, OpenAMSM integration and live 5GC scenarios remain NOT_RUN. The two examples must remain NOT_LINKABLE / NOT_QUALIFIED until those gates close.
