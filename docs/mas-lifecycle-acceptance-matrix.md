# MAS Modify / Release acceptance matrix

**Current status: SOURCE_STATIC_ONLY.** The v1alpha5 Scheme C Procedures, request
Schemas and predicates are authored. No trusted MAS Owner publication, Host /
Runtime acceptance or live 5GC E2E result is claimed for the CA-SL layer.

> Scope note: this matrix is the CA-SL authoring/qualification view. The real
> OpenAMSM 5GC E2E results (UE Modify/Release, PFCP reconcile, restart) live in
> `docs/scheme-c-3gpp-traceability.md` and are a **separate** verdict layer. A
> 5GC behaviour PASS is not a CA-SL Runtime PASS, and vice versa.

## Static source acceptance

| Check | Expected result | Current evidence |
| --- | --- | --- |
| CA-SL version | Both packages use connectionagent.io/v1alpha5 syntax only | Procedure / Contract / Predicate sources |
| Modify graph | `validate-modify-request` -> `parse-n1` -> `apply-qos-delta` -> `verify-modify-completion` | Static regression test |
| Release graph | `validate-release-request` -> `parse-n1` -> `build-command` -> `confirm-n1` -> `confirm-n2` -> `delete-policy` -> `delete-user-plane` -> `emit-release-event` -> `release-sm-context` -> `verify-release-completion` | Static regression test |
| Public request schemas | Modify requires `[pduSessionId, entryKind]`; Release requires `[pduSessionId, entryKind, trigger]`; both closed | Request Schemas + static regression test |
| Private payload fields | `n1Sm`, `releaseTxn` and `qosFlowsDelta` are not request fields; raw N1 and the release transaction are Host-private / Provider-injected | Request Schemas + [Owner contract](mas-lifecycle-owner-contract.md) |
| Release entry variant | `entryKind` is only `UE_INITIATED`; trigger is the numeric Owner enum 1..7 | Schema + Predicate test |
| Parse read-only | Both parse occurrences are READ: no `OUTCOME_UNKNOWN`; `FAILED`/`DENIED` terminate. The parse must not mutate session state | Procedure + static regression test |
| Mutation fail-closed | `apply-qos-delta`, `build-command`, `confirm-n1`, `confirm-n2`, `delete-policy`, `delete-user-plane`, `emit-release-event` and `release-sm-context` each have `OUTCOME_UNKNOWN: SAFE_STOPPED`, `FAILED:` and `DENIED:` | Procedure + static regression test |
| Success publication | Exactly one `PASS: SUCCEEDED`, only at the final postcondition | Static regression test |
| QoS delta target | `apply-qos-delta` compares the applied result field by field with the parsed Owner target (`qfi`, `five_qi`, `gfbr_ul`, `gfbr_dl`, `mfbr_ul`, `mfbr_dl`), plus the APPLIED dispatch state | Predicate positive/negative tests |
| Release predicate outputs | Predicates use only declared Owner outputs: `release_ready`, `n1_released`, `n2_released`, `terminated`, `released`, `last_event`, `lifecycle` | Predicate source + static regression test |
| Optional steps | Charging update/delete are omitted because no applicability predicate exists | Source mapping |
| Compensation | Compensation is `execute: skip`; no compensation / replan / retry is authored | Source mapping + static test |
| Owner publication | Missing trusted MAS ToolCatalog / CapabilityContracts / receipts remain fail-closed | Compiler gate |
| Synthetic contract closure | Both examples pass Check / Inspect / Build against the synthetic Owner fixture | Source Hygiene CI PASS; all reports remain NOT_QUALIFIED |

## Qualification scenario matrix

| Scenario | Required behavior | Status |
| --- | --- | --- |
| Modify success | `parse-n1` and `apply-qos-delta` settle for the same SUPI / PSI / generation; the applied target equals the parsed target and `qos_delta_state=APPLIED` with `n1n2_dispatched=1` | Owner-level Scheme C UE Modify PASS on the isolated `ac` stack (`env-5gc-sim` evidence `20261122-scheme-c-ue-modify/`, `20261122-scheme-c-relay-fail-closed/`); **CA-SL Runtime NOT_RUN** — the verdict layers are not merged |
| QoS delta target state | An independent `/pdu-info` read equals the requested QFI/5QI/GBR/MBR and the PFCP QER carries the same bitrates | Development E2E PASS (isolated stack); this is not the Skill Predicate |
| Parse read-only | The parse mutates no session state, binds no PTI and emits no mutation receipt | Owner unit / source inspection only; Host test NOT_RUN |
| UE-initiated Modify | Host authenticates a new UE UpdateSMContext business action | Host test NOT_RUN |
| AMF-initiated Modify | Host authenticates a new AMF business action, not a continuation callback | Host test NOT_RUN |
| Network-triggered Modify | Only a trusted internal Owner event may select this entry variant | Host test NOT_RUN |
| Release success | Parse, Build, both confirmations and the cleanup occurrences settle for the same SUPI / PSI / generation | **CA-SL Runtime NOT_RUN.** Owner-level Scheme C UE Release PASS on the isolated `ac` stack (`env-5gc-sim` evidence `20261123-scheme-c-reconcile/`, `20261123-scheme-c-release-conformance/`); not a CA-SL Runtime verdict |
| UE-initiated Release | `trigger=2`; matching N1/N2 release exchange completes | Owner-level Scheme C E2E PASS (`0xd1 -> 0xd3 -> 0xd4`, N2 REL CMD/RSP, PFCP 54/55, context removed); **CA-SL Host test NOT_RUN** |
| Build is the only PTI binding | The release parse does not bind the PTI; the Build occurrence is the single transaction-controlled binding and records the generation | Static source check; Owner / Host test NOT_RUN |
| Confirmation Run binding | A confirmation is bound to the original Run and its Build transaction / generation; duplicates, late answers and old generations are rejected | Owner / Host test NOT_RUN |
| AMF-initiated Release | Out of scope for this version; reported NOT_RUN / BLOCKED, never coerced | Host test NOT_RUN |
| Network-triggered Release | Out of scope for this version; reported NOT_RUN / BLOCKED, never coerced | Host test NOT_RUN |
| PFCP deletion | `delete-user-plane` returns `released=1` only after the matching PFCP delete completion | Owner-level PASS on the real `ac` stack; **CA-SL Owner test NOT_RUN** |
| PCF deletion | `delete-policy` distinguishes deleted from absent for the same Scope | Owner-level PASS on the real `ac` stack; **CA-SL Owner test NOT_RUN** |
| Release event | `last_event=1` proves only the local in-memory marker; no Status Notify claim | Source inspection only |
| DENIED | No Owner dispatch; first-step denial may end FAILED, later denial SAFE_STOPPED | Runtime NOT_RUN |
| OUTCOME_UNKNOWN | SAFE_STOPPED; no blind retry, compensation or new Run | Owner / Runtime NOT_RUN |
| Duplicate invocation | Exact replay returns the original result / receipt without a second mutation | Owner test NOT_RUN |
| Wrong generation | Reject a receipt or callback with a different private generation | Owner / Host test NOT_RUN |
| Late callback | Attach only to the original pending occurrence; never resume a newer Run | Owner / Host test NOT_RUN |
| Mixed UE | Same PSI across two SUPIs cannot cross-satisfy Scope or Evidence | Owner / Host test NOT_RUN |
| Establishment s10 callback | Resume the original Establishment Run; do not start Modify or Release | Host test NOT_RUN |
| ResourceMap tombstone | Host performs it only after exact Release settlement; it is not a Skill output | Host test NOT_RUN |

## Verification boundary

The repository regression test checks the Scheme C graph order and node ids, the
closed public request Schemas, parse read-only framing, fail-closed mutation
routes, the single final `PASS: SUCCEEDED`, the modify Target comparison, release
predicate output closure and the non-claims. It does not simulate Owner receipts,
callback races, generation isolation or a live network. No live 5GC E2E result is
claimed.

The CI workflow uses the released Compiler v2.0.2 to reject YAML / v1alpha5
grammar errors while requiring the expected missing-Owner dependency diagnostic.
It also fetches the ca-client-tools v0.3.0 candidate at pinned commit
`ff1dc3ef938ccd9594ce55d72986a67622c00921`, materializes a synthetic Owner /
Capability / Evidence fixture and runs Check, Inspect and Build for all three MAS
Skills. All three synthetic Builds pass; this proves only static link-shape
compatibility with synthetic data and does not produce trusted Owner artifacts or
qualify the real Provider.

All Owner publication, Host binding, Runtime, OpenAMSM integration and live 5GC
scenarios remain NOT_RUN. The two examples must remain NOT_LINKABLE /
NOT_QUALIFIED until those gates close.
