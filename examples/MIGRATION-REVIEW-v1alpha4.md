# PR #58 — CA-SL v1alpha4 business migration decision register

**Status: PROPOSED FOR BUSINESS OWNER REVIEW — NOT APPROVED; NOT_QUALIFIED.**

5GC Node granularity and standard mapping follow the [3GPP-first SMF Authoring Profile](../docs/authoring-5gc-3gpp-profile.md). The v1alpha4 candidate uses `holdRef` for an opaque Owner correlation handle; the legacy ToolCatalog `waiterRef` name is not treated as v1alpha4 authority, and no author-level Wait/Await/Poll Node is retained.
Normative CA-SL pin: `7f84393ee8c395e4d8c39a74cb5000a1f896588d`.
Independent code review: [PR #58 review #5911630734](https://github.com/odango-chan/ca-skills/pull/58#pullrequestreview-5911630734).

This record distinguishes **authoring design choices** in the PR from **unapproved Owner/runtime contracts**. It does **not** claim business Owner sign-off, tool existence, linked schemas, CI qualification, or 5GC/MAS operational behavior. Every historical Case remains a separate expectation; names and expected terminal must be revalidated before claiming parity.

## Proposed design decisions (pending Owner approval)

| Decision | Source mapping | Owner / validation gap |
|---|---|---|
| No author Wait | §21/§52: real asynchronous protocol completion inside matching Owner Operation, no `ca.session.evidence.await` | Tool Owner actual output, completion, Correlation, Deadline, Evidence, failure classes and snapshots not published |
| Step 8 + initial N4 | No separate Step 8 Script Node; `establish-n4-session` = `upn::UPN.CREATE_UP_SESSION` performs native SMF UPF/session-address selection and N4 establishment | UPN Owner must consume the exact admitted request, UDM subscription result and PCF policy result, and return the effective session configuration plus authoritative N4 result; contract not published |
| RAN acceptance | `complete-an-resource-setup` = `ssm::SSM.SIGNAL_UE_AN` (not AMF N1N2-transfer ACK) | SSM Provider contract not published |
| N4 forwarding | `modify-n4-session` = `upn::UPN.MODIFY_UP_SESSION` (not AMF ACK) | UPN mutation contract not published |
| Initial admission | CreateSMContext Request is the Host ingress trigger outside the Procedure; Host performs source/action/identity admission, duplicate suppression, business-instance association and lifecycle/correlation. The Skill's request-profile Precondition is on its first business Node | Host execution metadata remains private; only the subject `ueRef` projection is Skill-visible |
| 5GC business gates | UDM subscription/request compatibility, UDM subscription ownership, PCF association ownership, AMF transfer initiation and terminal resource responsibility remain explicit business proofs | UDM compatibility is a Step 4 Predicate Script; its Evidence binds the exact UDM query and returned subscription. PCF request derivation/governance remains internal to PCF Owner. Step 8 native UPF/address selection is internal to UPN Owner and is not a separate Skill Node |
| MAS business gates | Postcondition for each of 15 business Operations and separately for ca-compensate-confirmed-failure; original output dependencies restored | MAS ToolCatalog/evidence and data schemas not approved; flags are authoring hypotheses |
| Confirmed failure handoff / MAS ca-compensate-confirmed-failure | Business FAIL/FAILED may enter author `ca-transfer-failed-resource-responsibility` or MAS `ca-compensate-confirmed-failure` **only after** Owner proves the original attempted mutation resolved and ca-compensate-confirmed-failure/handoff authorized | Requires explicit owner contract, no automatic authority |
| Commit uncertainty | On `OUTCOME_UNKNOWN`, stop directly `SAFE_STOPPED`; **never** call ca-compensate-confirmed-failure/handoff or retry. Host retains immutable original call and pending resource responsibility | Host §12.7/§20 proof, post-stop retention and Late Result handling remain NOT_QUALIFIED |
| Actual terminal | §12.8 terminal priority `SAFE_STOPPED > UNRESOLVED > FAILED` determines final publication based on admitted resources/unknown status | A requested `FAILED` route may publish `SAFE_STOPPED`; trace and mismatch diagnostics still require runtime evidence |

**Important unresolved business checks:** an Operation `SUCCEEDED` and its candidate output is **not** assumed to satisfy the Predicate on its own. Especially legacy `sbi.pcf.sm_policy.create` and `sbi.amf.n1n2.transfer` still only prove their original service result, not N4/RAN convergence. The new UPN/SSM IDs are **target design references in §21**, not proof of published APIs. Predicate outputs from independent authoritative observations must not be forged by passing the previous Operation reply as an Observation result.

**Do not merge as qualified:** no runnable v1alpha4 Fixture or positive linked Build is available, no 36 conventional Case execution, no 6 MAS runtime acceptance. Before adoption: publish exact ToolCatalog/CapabilityContracts/Schema/Evidence, decide ca-compensate-confirmed-failure/terminal semantics and proof domains with business Owner, verify Stage routes, produce executable v1alpha4 fixtures, then run §45.2 CI/Host/5GC acceptance.

## Legacy Case inventory (mapping candidates only)

The following entries are one-to-one *traceability* rows, not converted fixtures or reproduced outcomes. All 42 are **NOT_RUN**. For each Case preserve historical expected business facts and terminal unless an explicitly approved business decision changes them.

### establish-pdu-session — 36 historical Cases

| Legacy Case | Candidate v1alpha4 point of responsibility | Result |
|---|---|---|
| [01-complete-profile](legacy/establish-pdu-session/cases/01-complete-profile/case.yaml) | verify-pdu-session-establishment; N4/RAN/managed ownership | NOT_RUN / Owner not linked |
| [02-ingress-unknown](legacy/establish-pdu-session/cases/02-ingress-unknown/case.yaml) | admit-create-sm-context-request global ingress/lifecycle | NOT_RUN / Owner not linked |
| [03-udm-partial-or-ambiguous](legacy/establish-pdu-session/cases/03-udm-partial-or-ambiguous/case.yaml) | get-sm-subscription-data + UDM producer Evidence | NOT_RUN / Owner not linked |
| [04-udm-target-rejection](legacy/establish-pdu-session/cases/04-udm-target-rejection/case.yaml) | get-sm-subscription-data + UDM producer Evidence | NOT_RUN / Owner not linked |
| [05-address-or-callback-missing](legacy/establish-pdu-session/cases/05-address-or-callback-missing/case.yaml) | ca-read-sm-operation-context / ca-prepare-pdu-session-establishment-accept | NOT_RUN / Owner not linked |
| [06-subscription-ownership-unknown](legacy/establish-pdu-session/cases/06-subscription-ownership-unknown/case.yaml) | subscribe-sm-data.postcondition / outcome unknown | NOT_RUN / Owner not linked |
| [07-pcf-association-reused](legacy/establish-pdu-session/cases/07-pcf-association-reused/case.yaml) | establish-sm-policy-association.postcondition / outcome unknown | NOT_RUN / Owner not linked |
| [08-initial-n4-not-proven](legacy/establish-pdu-session/cases/08-initial-n4-not-proven/case.yaml) | establish-n4-session-session (UPN.CREATE_UP_SESSION) | NOT_RUN / Owner not linked |
| [09-old-instance-or-no-authority](legacy/establish-pdu-session/cases/09-old-instance-or-no-authority/case.yaml) | ca-read-sm-operation-context.postcondition | NOT_RUN / Owner not linked |
| [10-response-artifact-invalid](legacy/establish-pdu-session/cases/10-response-artifact-invalid/case.yaml) | ca-build-n1n2-message / ca-prepare-pdu-session-establishment-accept | NOT_RUN / Owner not linked |
| [11-amf-202-unsupported](legacy/establish-pdu-session/cases/11-amf-202-unsupported/case.yaml) | admit-create-sm-context-request global ingress/lifecycle | NOT_RUN / Owner not linked |
| [12-ran-setup-failure](legacy/establish-pdu-session/cases/12-ran-setup-failure/case.yaml) | complete-an-resource-setup (SSM.SIGNAL_UE_AN) / confirmed FAIL vs UNKNOWN | NOT_RUN / Owner not linked |
| [13-ran-late-or-ambiguous](legacy/establish-pdu-session/cases/13-ran-late-or-ambiguous/case.yaml) | complete-an-resource-setup (SSM.SIGNAL_UE_AN) / confirmed FAIL vs UNKNOWN | NOT_RUN / Owner not linked |
| [14-n4-forwarding-failure](legacy/establish-pdu-session/cases/14-n4-forwarding-failure/case.yaml) | modify-n4-session (UPN.MODIFY_UP_SESSION) | NOT_RUN / Owner not linked |
| [15-no-ue-observation-required](legacy/establish-pdu-session/cases/15-no-ue-observation-required/case.yaml) | verify-pdu-session-establishment avoids unsupported UE-observation requirement | NOT_RUN / Owner not linked |
| [16-manager-receipt-missing](legacy/establish-pdu-session/cases/16-manager-receipt-missing/case.yaml) | ca-transfer-resource-responsibility/ca-transfer-failed-resource-responsibility; Host retains UNKNOWN | NOT_RUN / Owner not linked |
| [17-subscribe-sm-data-unknown](legacy/establish-pdu-session/cases/17-subscribe-udm-unknown/case.yaml) | subscribe-sm-data.postcondition / outcome unknown | NOT_RUN / Owner not linked |
| [18-establish-sm-policy-association-unknown](legacy/establish-pdu-session/cases/18-create-policy-unknown/case.yaml) | establish-sm-policy-association.postcondition / outcome unknown | NOT_RUN / Owner not linked |
| [19-response-prepare-denied](legacy/establish-pdu-session/cases/19-response-prepare-denied/case.yaml) | ca-prepare-pdu-session-establishment-accept.FAILED | NOT_RUN / Owner not linked |
| [20-transfer-to-amf-unknown](legacy/establish-pdu-session/cases/20-transfer-to-amf-unknown/case.yaml) | transfer-n1n2-message.OUTCOME_UNKNOWN → SAFE_STOPPED | NOT_RUN / Owner not linked |
| [21-handoff-success-unknown](legacy/establish-pdu-session/cases/21-handoff-success-unknown/case.yaml) | ca-transfer-resource-responsibility/ca-transfer-failed-resource-responsibility; Host retains UNKNOWN | NOT_RUN / Owner not linked |
| [22-handoff-failed-unknown](legacy/establish-pdu-session/cases/22-handoff-failed-unknown/case.yaml) | ca-transfer-resource-responsibility/ca-transfer-failed-resource-responsibility; Host retains UNKNOWN | NOT_RUN / Owner not linked |
| [23-denied-before-resource-create](legacy/establish-pdu-session/cases/23-denied-before-resource-create/case.yaml) | pre-Mutation FAILED terminal, not SAFE_STOPPED without resources | NOT_RUN / Owner not linked |
| [24-amf-200-still-buffered](legacy/establish-pdu-session/cases/24-amf-200-still-buffered/case.yaml) | transfer-n1n2-message.postcondition + complete-an-resource-setup; ACK != RAN adoption | NOT_RUN / Owner not linked |
| [25-handoff-unresolved-unknown](legacy/establish-pdu-session/cases/25-handoff-unresolved-unknown/case.yaml) | ca-transfer-resource-responsibility/ca-transfer-failed-resource-responsibility; Host retains UNKNOWN | NOT_RUN / Owner not linked |
| [26-handoff-success-not-committed](legacy/establish-pdu-session/cases/26-handoff-success-not-committed/case.yaml) | ca-transfer-resource-responsibility/ca-transfer-failed-resource-responsibility; Host retains UNKNOWN | NOT_RUN / Owner not linked |
| [27-handoff-failed-not-committed](legacy/establish-pdu-session/cases/27-handoff-failed-not-committed/case.yaml) | ca-transfer-resource-responsibility/ca-transfer-failed-resource-responsibility; Host retains UNKNOWN | NOT_RUN / Owner not linked |
| [28-handoff-unresolved-not-committed](legacy/establish-pdu-session/cases/28-handoff-unresolved-not-committed/case.yaml) | ca-transfer-resource-responsibility/ca-transfer-failed-resource-responsibility; Host retains UNKNOWN | NOT_RUN / Owner not linked |
| [29-lifecycle-not-ready](legacy/establish-pdu-session/cases/29-lifecycle-not-ready/case.yaml) | admit-create-sm-context-request global ingress/lifecycle | NOT_RUN / Owner not linked |
| [30-lifecycle-proof-unavailable](legacy/establish-pdu-session/cases/30-lifecycle-proof-unavailable/case.yaml) | admit-create-sm-context-request global ingress/lifecycle | NOT_RUN / Owner not linked |
| [31-read-only-unknown](legacy/establish-pdu-session/cases/31-read-only-unknown/case.yaml) | read-only UNKNOWN / §12.8 terminal priority | NOT_RUN / Owner not linked |
| [32-budget-after-subscribe](legacy/establish-pdu-session/cases/32-budget-after-subscribe/case.yaml) | limits.maxActions / Host budget enforcement | NOT_RUN / Owner not linked |
| [33-required-subscription-fields-missing](legacy/establish-pdu-session/cases/33-required-subscription-fields-missing/case.yaml) | get-sm-subscription-data + UDM producer Evidence | NOT_RUN / Owner not linked |
| [34-udm-producer-evidence-mismatch](legacy/establish-pdu-session/cases/34-udm-producer-evidence-mismatch/case.yaml) | get-sm-subscription-data + UDM producer Evidence | NOT_RUN / Owner not linked |
| [35-reconciled-commit-still-stops](legacy/establish-pdu-session/cases/35-reconciled-commit-still-stops/case.yaml) | Host Owner-only mutation.reconcile (no authored stage) | NOT_RUN / Owner not linked |
| [36-reconciled-not-committed-no-retry](legacy/establish-pdu-session/cases/36-reconciled-not-committed-no-retry/case.yaml) | Host Owner-only mutation.reconcile (no authored stage) | NOT_RUN / Owner not linked |


### establish-pdu-session-mas — 6 historical Cases

| Legacy Case | Candidate v1alpha4 point of responsibility | Result |
|---|---|---|
| [01-policy-first-happy](legacy/establish-pdu-session-mas/cases/01-policy-first-happy/case.yaml) | validate-sm-subscription → verify-pdu-session-establishment (positive path) | NOT_RUN / Owner not linked |
| [02-entry-eligibility-unknown](legacy/establish-pdu-session-mas/cases/02-entry-eligibility-unknown/case.yaml) | admit-create-sm-context-request.precondition: establishment.mas.eligible | NOT_RUN / Owner not linked |
| [03-policy-update-outcome-unknown](legacy/establish-pdu-session-mas/cases/03-policy-update-outcome-unknown/case.yaml) | modify-sm-policy-association.OUTCOME_UNKNOWN → SAFE_STOPPED; no ca-compensate-confirmed-failure mutation | NOT_RUN / Owner not linked |
| [04-namf-ack-without-ran-adoption](legacy/establish-pdu-session-mas/cases/04-namf-ack-without-ran-adoption/case.yaml) | complete-an-resource-setup.postcondition: ran_adopted (no ACK shortcut) | NOT_RUN / Owner not linked |
| [05-resource-handoff-missing](legacy/establish-pdu-session-mas/cases/05-resource-handoff-missing/case.yaml) | ca-transfer-resource-responsibility + verify-pdu-session-establishment.resources_managed | NOT_RUN / Owner not linked |
| [06-secondary-auth-required-out-of-profile](legacy/establish-pdu-session-mas/cases/06-secondary-auth-required-out-of-profile/case.yaml) | resolve-secondary-authentication.postcondition (confirmed auth restriction) | NOT_RUN / Owner not linked |


## Outstanding review gates

- [ ] Business Owner approves each proposed 5GC and MAS authoring mapping, resource lifecycle and definitive failure/unknown handling.
- [ ] Exact UPN/SSM/MAS/Host Owner snapshots and Capability grants are published and verified; no `urn:example` aliases in a successful link.
- [ ] Script F.6 parser / strict TypedDict assignability tests run in actual Compiler Native/WASM (repository-local type lint is not conformance).
- [ ] All 36 conventional Cases transformed into executable v1alpha4 fixtures and run; 6 MAS cases retain separate unqualified design obligations.
- [ ] Native/WASM/Studio, Host/Runtime, Trace and live 5GC §45.2 proof or explicit NOT_QUALIFIED status.
