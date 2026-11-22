# Scheme C UE Modify / Release — 3GPP → CA-SL → MAS → Source Traceability (DRAFT)

**Status: SOURCE-ALIGNED DRAFT — NOT_QUALIFIED — NOT_LINKABLE.**
This is the traceability document for the current Scheme C implementation. It
is **not** an Owner publication, **not** a
trusted ToolCatalog / CapabilityContract, **not** a Runtime or Host acceptance
result, and **not** a product qualification statement.

Hard rules applied in this document:

- No fabricated PASS. Every verdict is copied from a real evidence artifact that
  the reader can open, or it is `NOT_RUN` / `BLOCKED` / `FAIL`.
- `Accepted != implemented != PASS != VERIFIED`.
- A passing 5GC protocol/behavior gate on the Owner + Mock-AMF stack is **not**
  a CA-SL Skill/Runtime PASS. The two verdict layers are kept in separate
  columns.
- Spec clause numbers are verified against the ETSI PDFs listed in §2.3 for the
  procedures used here. Anything not listed there is marked `UNVERIFIED`; a
  repository comment citing a clause is labelled *repo-cited* and is not spec
  verification.
- The legacy OES mapping (pins `env-openamsm@594dec78`, plans `pdu-mod-v3` /
  `pdu-rel-v4`) is **HISTORICAL**. It is not the current execution order and
  must not be read as such (see §5).

---

## 0. Locator conventions and build identity

### 0.1 Repositories

| Alias used below | Path | Identity observed this session |
| --- | --- | --- |
| `OWNER` | `env-openamsm-qdelta/` | PR #21, branch `feat/owner-qos-delta`, HEAD `c4f2fb2` (commit body enumerates patches `0015`–`0019`), plus **untracked** working patches `0020`–`0021` in `patches/openamsm/`; built tree `build/openamsm-source/` |
| `PEER` | `.agent-tmp/runtime-consumers/ca-5gc-sim/` (= `env-5gc-sim`) | PR #79; branch observed as `feat/d5-ue-modify-peer` |
| `CASL` | `ca-skills/` | CA-SL v1alpha5 docs + example Skill packages |

Cross-repo locators are written as `OWNER:<path>`, `PEER:<path>`,
`CASL:<path>`. `build/openamsm-source/` is a **generated** tree
(`./bin/env-openamsm build` re-materialises it from
`OWNER:upstream/openamsm/` + `OWNER:patches/openamsm/*`). The canonical change is
the patch file; line numbers below were read from the generated tree during this
session (2026-11-22). **Line numbers in that tree drift** — it is regenerated
under the working session — so prefer `function name` + patch file when citing
across time; a re-read during this session already shifted `orch_engine.py`
anchors by +13 lines.

### 0.2 Build identity — what the evidence actually covers

| Evidence set | Owner build identity | Notes |
| --- | --- | --- |
| `PEER:artifacts/acceptance/20261122-scheme-c-release-reliability/` | base `efb5d17` + patches `0001`,`0006`–`0019`; `build_patch_identity = d17699bf3fe8198076bafb8c1c491b85b8e7e8dd00176e0912465fd93207502e` | matches HEAD `c4f2fb2` content (0015–0019 are squashed into HEAD) |
| `PEER:artifacts/acceptance/20261123-scheme-c-reconcile/` | `build_patch_identity = 1f0b52ba9c9acc8497a06bada5d79cb3e4b228416d95de8a788963df40e50948`; patches `0001`, `0006`–`0021` (includes `0020` UPF `/session-info`, `0021` reconcile/restart) | committed evidence; `build-identity.json` + `run-manifest.json` + `SHA256SUMS` |
| current `OWNER:build/openamsm-source/` | HEAD + untracked `0020`, `0021` | contains `src/upf/session-info.c` and `src/smf/mas/common/mas-reconcile-sbi.c` |

**Traceability defect (reported, not fixed):** `PEER:artifacts/acceptance/20261122-scheme-c-release-reliability/build-identity.json`
records `source.tree_sha256 = 7dfe5a3db4d4bc920bfaa7b844b80336698f90f6c7086b060b93afa4c8556c8d`,
which is byte-identical to the **pristine upstream import** digest documented in
`OWNER:docs/upstream.md:14` (imported 2026-11-16, before any patch existed).
A patched tree cannot hash to the pristine digest, so `tree_sha256` in that
artifact does **not** identify the build under test. The only distinguishing
field is `build_patch_identity` plus the enumerated patch list. Any consumer that
keys on `tree_sha256` will wrongly conclude the evidence was produced on
unpatched source. → treat `build_patch_identity` as authoritative and treat
`tree_sha256` as `UNVERIFIED`/suspect until recomputed.

---

## 1. Scope

In scope:

1. UE-requested PDU Session Modification (N1 `0xC9`).
2. UE-requested PDU Session Release (N1 `0xD1`, confirmations `0xD4` /
   N2 `PDU_RES_REL_RSP`).
3. Establishment as the controlling pre-condition (not re-verified this round).
4. AMF-requested `ReleaseSMContext` — **mapping only**.
5. SMF-initiated release — **mapping + gap only**.

Out of scope for this round: Network-requested `ReleaseSMContext`
(`OWNER` issue #10), any change to CA-SL v1alpha5 language or the Compiler,
any merge/tag/release.

---

## 2. Verified spec baseline (Release 19)

### 2.1 Versions and dates actually verified

Verified against the ETSI deliver directory listings (the directory timestamp is
the ETSI publication/upload time of that version). This is a **version-level**
verification only.

| Spec | Rel-19 version | ETSI publish timestamp | Verification URL |
| --- | --- | --- | --- |
| TS 23.502 | **19.9.0** | 2026-10-02 | <https://www.etsi.org/deliver/etsi_ts/123500_123599/123502/> |
| TS 23.501 | **19.9.0** | 2026-10-02 | <https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/> |
| TS 24.501 | **19.8.0** | 2026-10-12 | <https://www.etsi.org/deliver/etsi_ts/124500_124599/124501/> |
| TS 29.502 | **19.8.0** | 2026-10-09 | <https://www.etsi.org/deliver/etsi_ts/129500_129599/129502/> |
| TS 29.518 | **19.8.0** | 2026-10-09 | <https://www.etsi.org/deliver/etsi_ts/129500_129599/129518/> |
| TS 29.244 | **19.6.0** | 2026-08-11 | <https://www.etsi.org/deliver/etsi_ts/129200_129299/129244/> |
| TS 29.503 | **19.7.0** | 2026-08-13 | <https://www.etsi.org/deliver/etsi_ts/129500_129599/129503/> |
| TS 29.512 | **19.7.0** | 2026-07-01 | <https://www.etsi.org/deliver/etsi_ts/129500_129599/129512/> |
| TS 29.571 | **19.8.0** | 2026-10-09 | <https://www.etsi.org/deliver/etsi_ts/129500_129599/129571/> |

Cross-check on the 3GPP archive (independent of ETSI), for the two governing
stage-2 specs: `23502-j90.zip` and `23501-j90.zip` (`j` = Rel-19, `90` =
19.9.0) listed in
<https://www.3gpp.org/ftp/Specs/latest/Rel-19/23_series/> with file timestamps
2026-09-24. Version agreement confirms 19.9.0; the upload-date difference
(2026-09-24 3GPP vs 2026-10-02 ETSI) is expected replication lag.

### 2.2 What "verified" means here, precisely

- **Verified:** the Rel-19 version number and the ETSI publication timestamp of
  each of the nine specs.
- **Not verified:** any *content* of these specs — no clause text, heading
  number, table, or step ordering was read.

### 2.3 Clause-level verification (verified this session)

The ETSI PDFs were downloaded directly and their text extracted (ETSI requires
a browser-like User-Agent; the earlier 406 was a client issue, not an access
restriction). The following clause/step attributions were read in the PDF
text and are therefore **verified**, not remembered:

| Spec (version) | Clause / table read | Used for |
| --- | --- | --- |
| TS 23.502 19.9.0 | 4.3.2.2.1, steps 1, 3, 10a/10b, 11, 16a/16b | Establishment ingress, N4 establishment, N1/N2 transfer |
| TS 23.502 19.9.0 | 4.3.3.2, steps 1a, 2, 3b, 7a/7b, 8a/8b, 11a/11b, 12a/12b | UE Modify parse, PCF/N4 update, N1/N2 Modify, N2 response |
| TS 23.502 19.9.0 | 4.3.4.2, steps 1a, 1c, 1e, 2a/2b, 3, 4, 5, 6, 7a/7b, 9, 10a/10b, 12, 14, 15 | UE Release, AMF `ReleaseSMContext`, N4 release, finalize |
| TS 24.501 19.8.0 | 8.3.7 (Modification Request), 8.3.9 (Modification Command), 8.3.12 (Release Request), 8.3.14 (Release Command), 8.3.15 (Release Complete) | NAS message names and direction |
| TS 29.502 19.8.0 | Table 5.2.1-1; 5.2.2.2 Create SM Context; 5.2.2.3 Update SM Context; 5.2.2.4 Release SM Context | Service operation names/semantics |
| TS 29.518 19.8.0 | 5.2.2.3.1 `N1N2MessageTransfer` | `Namf_Communication_N1N2MessageTransfer` |
| TS 29.244 19.6.0 | 6.3.4 PFCP Session Deletion Procedure; 7.5.6 Request; 7.5.7 Response | N4 Session Release messages |

**Not content-verified** (version only): TS 23.501 19.9.0, TS 29.503 19.7.0,
TS 29.512 19.7.0, TS 29.571 19.8.0. Any clause number from those specs is
marked `UNVERIFIED` below. Message *names* still come from the implementation
and the verified specs above.

Where a repository source file itself cites a clause it is marked
**`repo-cited, unverified`** and attributed; that is an upstream Open5GS
comment, not a verification.

---

## 3. Current Scheme C implementation inventory

### 3.1 Entry routing — `OWNER:build/openamsm-source/tools/nw-agent/server.py`

| Concern | Locator | Behaviour |
| --- | --- | --- |
| Scheme C facade gate | `server.py:735-742` | `OPENAMSM_PLAN_PROVIDER=agent_step` required, else `503 AGENT_STEP_REQUIRED` |
| Create (Establish) | `server.py:744-780` | `POST /nsmf-pdusession/v1/sm-contexts`; plan `ESTABLISH_POLICY_FIRST` → `ESTABLISH`; `run_plan` |
| Modify/Release dispatch | `server.py:795-800` | path must be `.../sm-contexts/{ref}/(modify OR release)` |
| Lost association | `server.py:532-600` | release-shaped → `409 OUTCOME_UNKNOWN` with `retryable:false`; completed tombstone → `409 RELEASE_COMPLETED`; non-release-shaped → `404 SESSION_ASSOC_NOT_FOUND` |
| N2 modify continuation | `server.py:807-815` | `PDU_RES_MOD_RSP` in body → `forward_to_smf` (native continuation, not a new entry) |
| N1 `0xD1` | `server.py:829-846` | `run_c_release_request` → `_build_ue_release_answer` |
| N1 `0xD4` | `server.py:851-860` | `run_c_release_confirm(entry,"n1")` |
| N2 `PDU_RES_REL_RSP` | `server.py:864-870` | `run_c_release_confirm(entry,"n2")` |
| N1 `0xC9` | `server.py:873-880` | `run_c_modify` |
| `/release` (AMF) | `server.py:928-951` | **legacy** OES plan `RELEASE` with `start_inputs={"trigger":"6"}` — not Scheme C |
| Legacy modify fallback | `server.py:952-960` | OES plan `MODIFY` |
| Admin recovery | `server.py:1050-1075` | `POST /nnwagent-admin/v1/release-recovery` → `recover_release` |
| Observability | `server.py:1021` | `GET /admin/statez` (counts, per-assoc `releasePhase`) |

### 3.2 Orchestration engine — `OWNER:build/openamsm-source/tools/nw-agent/orch_engine.py`

| Symbol | Locator | Behaviour |
| --- | --- | --- |
| `_unknown_status` | `orch_engine.py:50-52` | `>=500` or `0` ⇒ `OUTCOME_UNKNOWN` |
| `invoke_mas` | `orch_engine.py:365-...` | `POST /nsmf-mas-orchestration/v1/invoke` with `sessionRef/stepId/mas/op/inputs/idempotencyKey` |
| `run_c_modify` | `orch_engine.py:850-895` | N1 `0xC9` validate → `SSM.SIGNAL_UE_AN{parse_n1}` → `UPN.MODIFY_UP_SESSION{qos_flows_delta}` |
| `_release_step` | `orch_engine.py:897-928` | writes ledger row as `UNKNOWN` **before** the call; outcome `OK/FAILED/UNKNOWN` after |
| `_release_cleanup` | `orch_engine.py:940-977` | order `r-pa` → `r-upn` → `r-se` → `r-sc`; **`trigger` hardcoded `"2"`** (`:948`) |
| `run_c_release_request` | `orch_engine.py:979-1066` | `0xD1` → SSM parse → SSM build (`mode=build`) → returns N1/N2 hex; sets phase `COMMAND_SENT` |
| `run_c_release_confirm` | `orch_engine.py:1068-1136` | `0xD4`/N2 → SSM confirm; only when `release_ready==1` runs cleanup; sets `CLEANING`→`COMPLETED`/`UNKNOWN`/`FAILED` |
| `recover_release` | `orch_engine.py:1181-1339` | operator recovery: requires `confirm="RECOVER"`, owner-observed generation/txn/N1+N2/PFCP state; can only re-run `r-sc` |
| test seam | `orch_engine.py` `OPENAMSM_AGENT_TEST_KILL_AT` | kill points `after_build`, `before_cleanup`, `during_cleanup_pfcp`, `before_sc_finalize`; empty in normal operation |

### 3.3 Owner MAS capabilities

| MAS / op | Source | Notes |
| --- | --- | --- |
| Catalog op enum + names | `OWNER:build/openamsm-source/src/smf/mas/common/mas-types.h:97-130`, `src/smf/oes/catalog.c:19-52` | `UPDATE_SM_CONTEXT`, `RELEASE_SM_CONTEXT`, `MODIFY_UP_SESSION`, `DELETE_UP_SESSION`, `SIGNAL_UE_AN`, `EMIT_EVENTS`, `DELETE_SM_POLICY`, `COMPENSATE_RELEASE` |
| MAS→NF mapping | `src/smf/oes/catalog.c:105-158` | `RELEASE_SM_CONTEXT`→SC, `DELETE_SM_POLICY`→PA, `DELETE_UP_SESSION`/`MODIFY_UP_SESSION`→UPN, `SIGNAL_UE_AN`→SSM, `EMIT_EVENTS`→SE |
| Dispatch | `src/smf/mas/common/mas-facade.c:207-330` | per-op invoke; `SIGNAL_UE_AN` with `release=1` routes to `mas_ssm_signal_release_invoke` (`:287-294`) |
| SSM release build | `src/smf/mas/ssm/ssm_ue.c:236-303` | builds N1 Release Command (5GSM `0xD3` = 211) + N2 `PDU_RES_REL_CMD`; increments generation; one command per generation; **forces `delete_trigger`/`sc.trigger` to `UE_REQUESTED`** (`:289-290`) |
| SSM trigger skip branch | `src/smf/mas/ssm/ssm_ue.c:339-347` | AMF Release / AMF Update / LOCAL → OK with **no** N1/N2 |
| SSM confirm | `src/smf/mas/ssm/ssm_ran.c:386-435` | binds `release_confirm` to exact `release_txn` + `release_generation`; duplicate/out-of-order/generation mismatch ⇒ `E_VALIDATE`; emits `release_ready` |
| SSM N1 parse | `src/smf/mas/ssm/ssm_ran.c:316-381` (release), `:197-...` (modify) | `0xD1` → `release_intent=ue_requested`; else falls through to modify parse |
| PA delete | `src/smf/mas/pa/policy_adapter.c:146-241` | PCF association delete; `pcfDeleteOutstanding` observable |
| UPN delete + PFCP state | `src/smf/mas/upn/upnode.c:94-213` | `pfcp_del_state ∈ NONE/IN_FLIGHT/ACCEPTED/REJECTED/UNKNOWN`; `mas_upnode_pfcp_del_complete(accepted)`, `..._unknown()` |
| UPN finalize gate | `src/smf/mas/upn/upnode.c:388-397` | finalize refused while deletion in flight/unknown |
| UPN modify / QoS delta | `src/smf/mas/upn/upnode.c:70-93`, `1424-...` | `MAS invoke` with `qos_flows_delta`; parks on PFCP + N1N2 dispatch |
| SC release | `src/smf/mas/sc/session_context.c:562-622`, `711-739` | `lifecycle=RELEASING`; phases: UDM SDM unsubscribe → UDM UECM deregister → ACK AMF; `rel_commit_phase` observable |
| Finalize + clear | `src/smf/mas/common/mas-orchestration-sbi.c:281-360` | `finalize=1` requires success **and** `mas_upnode_release_finalize_allowed`; else logs `release finalize fails closed` and keeps session |
| Success predicate | `src/smf/mas/common/mas-facade.c:72-113` | success = `STATUS_OK && error_code==OK`; mixed pair ⇒ `E_MAS`, never 200 |
| QueryContext SBI | `src/smf/mas/common/mas-context-query-sbi.c:45-90`, `:512-520` | `POST /nsmf-{sc,pa,upn,ssm,...}-context/v1/query` |
| PFCP reconcile SBI | `src/smf/mas/common/mas-reconcile-sbi.c:626-681` | `POST /nsmf-upn-context/v1/reconcile`; required body: `supi/pduSessionId/masStepId/masCorrId/n4Seid/upfId/expectedDeleteState` (`:310-315`); `expectedDeleteState` must be `UNKNOWN`; evidence `UPF_OBSERVATION` or `OPERATOR_ASSERTED` (`:421-433`, `:501-505`) |
| SE emit | `src/smf/mas/se/session_exposure.c:13-66` | in-memory marker only |

### 3.4 Implementation-type definitions used in §4

| Type | Meaning |
| --- | --- |
| `3GPP_NATIVE` | A 3GPP-defined operation/message implemented by the NF itself (SBI resource, NAS/NGAP codec) with no CA-specific indirection. |
| `CA_ADAPTER` | A CA-owned translation layer that maps a 3GPP-standard event onto Owner MAS invocations (the NW-Agent Scheme C facade, the MAS facade dispatch). |
| `CA_EXTENSION` | Owner-private capability with **no** 3GPP counterpart: QueryContext, PFCP reconcile, `release-recovery`, idempotency/ledger, tombstones, `finalize` flag. |

---

## 4. Mapping matrix

Column key — **Verdict (5GC)** is the Owner+Mock-AMF behavioural gate from
`PEER:.../20261122-.../evidence.md`; **Verdict (Skill)** is the CA-SL
Skill/Runtime layer, where nothing has ever been executed.
`§clause` is verified for TS 23.502/24.501/29.502/29.518/29.244 as listed in
§2.3; TS 23.501/29.503/29.512/29.571 clause numbers remain `UNVERIFIED`.

### 4.1 PDU Session Establishment (context row)

| # | 3GPP procedure / message (§clause) | CA-SL Procedure Node | MAS capability / operation | OpenAMSM source | Impl type | Success / failure / UNKNOWN | Evidence | Verdict (5GC) | Verdict (Skill) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | `Nsmf_PDUSession_CreateSMContext`; NAS PDU Session Establishment Request (TS 23.502 §4.3.2.2.1 step 1; TS 29.502 §5.2.2.2) | `establish-pdu-session-mas` (s0…s13, not re-scoped here) | plan `ESTABLISH_POLICY_FIRST` → `s1..s13` | `OWNER:tools/nw-agent/server.py:744-780` | `CA_ADAPTER` (3GPP_NATIVE ingress) | 201 + Location; failure ⇒ problem+json; a `SIGNAL_UE_AN` park continues in a daemon thread | `PEER:.../runs/normal/scenario.yaml`, `PEER:.../runs/normal/mas-trace.ndjson` (establish spans) | **NOT_RUN** (no dedicated gate; only `base_mock_status: PASS` as a pre-condition) | **NOT_RUN** |
| A2 | Establishment step sequence (SC.VALIDATE_SUBSCRIPTION → SC.CREATE_SM_CONTEXT → SC.REGISTER_UECM → PA.CREATE_SM_POLICY → CA.CREATE_CHARGING → UPS.DECIDE_ANCHOR → IAM.ALLOCATE_ADDRESS → IAM.CONFIRM_ADDRESS → UPN.CREATE_UP_SESSION → SSM.SIGNAL_UE_AN → UPN.MODIFY_UP_SESSION → SC.COMMIT_CONTEXT → SE.EMIT_EVENTS) (TS 23.502 §4.3.2.2.1 steps 3–17) | `sN` nodes | as listed | `OWNER:tools/nw-agent/plans/establish/*`, trace spans `OWNER` `src/smf/mas/*` | `CA_ADAPTER` | step failure ⇒ plan compensation or `D18` fail; `CA.CREATE_CHARGING` = `NOT_IMPL_skip` | `PEER:.../runs/normal/mas-trace.ndjson` | **NOT_RUN** | **NOT_RUN** |

Note: the Establishment `SE.EMIT_EVENTS`/`UPN.MODIFY_UP_SESSION` occurrences are
**distinct** from the Modify/Release occurrences and are not reusable
(`CASL:docs/mas-lifecycle-source-mapping.md:39-47`).

### 4.2 UE-requested PDU Session Modification

| # | 3GPP procedure / message (§clause) | CA-SL Procedure Node | MAS capability / operation | OpenAMSM source | Impl type | Success / failure / UNKNOWN | Evidence | Verdict (5GC) | Verdict (Skill) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | `Nsmf_PDUSession_UpdateSMContext` + NAS PDU Session Modification Request (`0xC9` = 201) (TS 23.502 §4.3.3.2 step 1a; TS 24.501 §8.3.7; TS 29.502 §5.2.2.3) | `modify-pdu-session-mas` entry (`validate-modify-request`) | (entry only) | `OWNER:tools/nw-agent/server.py:873-880` | `3GPP_NATIVE` ingress + `CA_ADAPTER` | PSI mismatch ⇒ `409 SESSION_CONFLICT`; non-`0xC9` ⇒ other branches | `PEER:.../runs/relay-accept/mas-trace.ndjson` | **PASS** (`SCHEME_C_UE_MODIFY_POSITIVE`) | **NOT_RUN** |
| B2 | NAS Modify Request QoS-flow-descriptions parse (TS 24.501 §8.3.7.8; TS 23.502 §4.3.3.2 step 1a) | m4 `SSM.SIGNAL_UE_AN_MODIFY` (source branch: parse) | `SSM.SIGNAL_UE_AN` with `parse_n1=1`,`n1_sm=<hex>` | `OWNER:src/smf/mas/ssm/ssm_ran.c:197-...` (called via `ssm_ue.c:459-464`) | `CA_ADAPTER` | returns `qfi/five_qi/gfbr_*/mfbr_*/requested_kind`; no `qfi` ⇒ `502 OWNER_PROTOCOL_INVALID` (`orch_engine.py:878-880`) | `PEER:.../runs/relay-accept/mas-trace.ndjson` (inputs `2e0601c9…`, outputs `qfi=1,five_qi=9,gfbr_ul=200000…`) | **PASS** (inside the same gate) | **NOT_RUN** |
| B3 | PDU Session Modification / PFCP QER update + N1/N2 Modify dispatch (TS 23.502 §4.3.3.2 steps 2, 3b, 8a/8b; TS 29.244 §7.5.4; TS 29.518 §5.2.2.3.1) | m5 `UPN.MODIFY_QOS_FLOWS` | `UPN.MODIFY_UP_SESSION` `{qos_flows_delta=1, qfi, five_qi, gfbr_ul, gfbr_dl, mfbr_ul, mfbr_dl}` | `OWNER:src/smf/mas/upn/upnode.c:70-93`, `:1424-...`; caller `orch_engine.py:881-886` | `CA_ADAPTER` | parked (`result=8`/`E_WAIT`) until PFCP QER accepted **and** N1/N2 dispatched; `APPLIED`/`ALREADY` reported by the source, **not** RAN acceptance | `PEER:.../runs/relay-accept/run-manifest.json` (QoS 200/400/500/1000 in `/pdu-info`), PFCP 52/53 in `PEER:.../runs/relay-accept/pfcp.pcap` | **PASS** (`SCHEME_C_UE_MODIFY_POSITIVE`) | **NOT_RUN** |
| B4 | N2 PDU Session Resource Modify Response continuation (TS 23.502 §4.3.3.2 steps 7a/7b; TS 29.502 §5.2.2.3) | — (native continuation, not a Node) | none (forwarded to SMF) | `OWNER:tools/nw-agent/server.py:807-815` | `3GPP_NATIVE` | forwarded verbatim; must not re-complete the MAS invoke (`CASL:docs/mas-lifecycle-owner-contract.md:76-80`) | `PEER:.../runs/relay-accept/nw-agent.log` | **PASS** (`SCHEME_C_RELAY_FAIL_CLOSED` covers accept/reject/hang) | **NOT_RUN** |

### 4.3 UE-requested PDU Session Release (the Scheme C implementation under review)

| # | 3GPP procedure / message (§clause) | CA-SL Procedure Node | MAS capability / operation | OpenAMSM source | Impl type | Success / failure / UNKNOWN | Evidence | Verdict (5GC) | Verdict (Skill) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | `Nsmf_PDUSession_UpdateSMContext` + NAS PDU Session Release Request (`0xD1` = 209) (TS 23.502 §4.3.4.2 steps 1a, 1e; TS 24.501 §8.3.12; TS 29.502 §5.2.2.3) | r2 gate (conceptually; see §5 divergence) | (entry only) | `OWNER:tools/nw-agent/server.py:829-846` → `orch_engine.py:979-1066` | `3GPP_NATIVE` ingress + `CA_ADAPTER` | `phase != IDLE` ⇒ `409 RELEASE_IN_PROGRESS`; `phase == UNKNOWN` ⇒ `409 OUTCOME_UNKNOWN`; PSI mismatch ⇒ `409 SESSION_CONFLICT`; bad EPD/type ⇒ `400 INVALID_N1` | `PEER:.../runs/normal/`, `PEER:.../runs/negative/` | **PASS** (`SCHEME_C_UE_RELEASE_POSITIVE`, `..._ORDERING_AND_DUPLICATES`) | **NOT_RUN** |
| C2 | UE release intent parse (TS 24.501 §8.3.12; TS 23.502 §4.3.4.2 step 1a) | r3 (source branch: parse) | `SSM.SIGNAL_UE_AN{parse_n1=1}` | `OWNER:src/smf/mas/ssm/ssm_ran.c:316-381` | `CA_ADAPTER` | requires `release_intent=ue_requested` + numeric `psi`/`pti`; else `502` / `409 RELEASE_CORRELATION` (`orch_engine.py:1022-1028`) | `PEER:.../runs/normal/mas-trace.ndjson` | **PASS** | **NOT_RUN** |
| C3 | SMF builds N1 Release Command (`0xD3`=211) + N2 PDU Session Resource Release Command (TS 23.502 §4.3.4.2 steps 3–5; TS 24.501 §8.3.14) | r3 (source branch: build) | `SSM.SIGNAL_UE_AN{release=1, mode=build, trigger=2, release_txn}` | `OWNER:src/smf/mas/ssm/ssm_ue.c:236-303` | `CA_ADAPTER` | one command per generation (`release_in_progress` OR `release_command_built` ⇒ `E_VALIDATE`); returns `n1_sm_hex`,`n2_sm_hex`,`release_generation`; Agent answers `200` multipart per TS 29.502 shape (`server.py:631-676`) | `PEER:.../runs/normal/mas-trace.ndjson` (`release_command_built`), `PEER:.../runs/normal/mock-amf.log` | **PASS** | **NOT_RUN** |
| C4 | N1 Release Complete (`0xD4`=212) **and** N2 `PDU_RES_REL_RSP` confirmations (TS 23.502 §4.3.4.2 steps 6, 7a/7b, 9, 10a/10b; TS 24.501 §8.3.15) | r3 → completion | `SSM.SIGNAL_UE_AN{release_confirm=n1-or-n2, release_txn, release_generation}` | `OWNER:src/smf/mas/ssm/ssm_ran.c:386-435`; Agent `orch_engine.py:1068-1136` | `CA_ADAPTER` | bound to exact txn+generation; duplicate / late / out-of-order ⇒ `E_VALIDATE` → `409 RELEASE_CONFIRM_REJECTED`; only `release_ready==1` proceeds | `PEER:.../runs/negative/` (early `0xD4`, N2-first, duplicate N1/N2) | **PASS** (`SCHEME_C_UE_RELEASE_ORDERING_AND_DUPLICATES`) | **NOT_RUN** |
| C5 | Policy termination (TS 23.502 §4.3.4.2 step 12) — cleanup step 1 | r4 `PA.DELETE_SM_POLICY` (executed position differs, §5) | `PA.DELETE_SM_POLICY{release=1,trigger=2}` | `OWNER:src/smf/mas/pa/policy_adapter.c:146-241`, `:420-...`; step `orch_engine.py:950` | `CA_ADAPTER` | parked on PCF delete (`pcfDeleteOutstanding`); non-2xx ⇒ cleanup stops, `FAILED` or `UNKNOWN` (`orch_engine.py:960-971`) | `PEER:.../runs/normal/mas-trace.ndjson` (`PA→PCF DELETE_SM_POLICY step=r-pa`) | **PASS** | **NOT_RUN** |
| C6 | User-plane release / PFCP Session Deletion (TS 23.502 §4.3.4.2 steps 2a/2b; TS 29.244 §6.3.4, §7.5.6, §7.5.7) — cleanup step 2; **order deviation, §5.2** | r2 `UPN.DELETE_UP_SESSION` | `UPN.DELETE_UP_SESSION{trigger=2}` | `OWNER:src/smf/mas/upn/upnode.c:94-213`; step `orch_engine.py:951` | `CA_ADAPTER` | `released=1` only after PFCP deletion completes; timeout ⇒ `pfcp_del_state=UNKNOWN`, never retried | `PEER:.../runs/normal/` (PFCP 54/55), `PEER:.../runs/timeout/` | **PASS** (`SCHEME_C_UE_RELEASE_POSITIVE`, `SCHEME_C_PFCP_DELETION_TIMEOUT`) | **NOT_RUN** |
| C7 | Release event marker (no 3GPP message) | r6 `SE.EMIT_RELEASE_EVENT` | `SE.EMIT_EVENTS{ev=RELEASED}` | `OWNER:src/smf/mas/se/session_exposure.c:13-66`; step `orch_engine.py:952` | `CA_EXTENSION` (Owner-private marker; no 3GPP message) | in-memory only; no output fields exposed | `PEER:.../runs/normal/mas-trace.ndjson` (`SE EMIT_EVENTS RELEASED`) | **PASS** | **NOT_RUN** |
| C8 | SM context release + finalize (TS 23.502 §4.3.4.2 steps 14, 15; 29.503 clause UNVERIFIED) — cleanup step 3 (last) | r5 `SC.RELEASE_SM_CONTEXT` | `SC.RELEASE_SM_CONTEXT{release=1, finalize=1, trigger=2}` | `OWNER:src/smf/mas/sc/session_context.c:562-622`; `mas-orchestration-sbi.c:281-360`; step `orch_engine.py:953-954` | `CA_ADAPTER` + `CA_EXTENSION` (`finalize`) | `lifecycle=RELEASING`; UDM SDM unsubscribe → UDM UECM deregister → ACK AMF; context cleared **only** on success **and** PFCP gate; failure ⇒ session retained, Agent maps to `UNKNOWN` (`504 completedSteps=[r-pa,r-upn,r-se]`) | `PEER:.../runs/finalize-failure/` (UDM killed; `mas-trace` shows `RELEASE_SM_CONTEXT → DEREGISTER_UECM`, `E_MAS`, `failedStep=r-sc`) | **PASS** (`SCHEME_C_RELEASE_FINALIZE_FAILURE_INJECTION`) | **NOT_RUN** |
| C9 | Interruption / lost association (no 3GPP procedure; `CA_EXTENSION`) | terminal routes (`SAFE_STOPPED` in the Skill) | none (no Owner mutation) | `OWNER:tools/nw-agent/server.py:532-600`, `orch_engine.py:1181-1339` | `CA_EXTENSION` | restart ⇒ `409 OUTCOME_UNKNOWN`, no replay, no rebuilt command, context retained; operator recovery only if Owner proves gen/txn/N1+N2/`ACCEPTED` | `PEER:.../runs/restart-{after_build,before_cleanup,during_cleanup_pfcp,before_sc_finalize}/checks.json` | **PASS** (4 gates) — but `after_build` is **inherently unrecoverable** (§8) | **NOT_RUN** |
| C10 | Concurrent session isolation (no 3GPP step; `CA_EXTENSION`) | — | — | assoc index `supi+psi`, `psi` reuse guard (`orch_engine.py:520-538`) | `CA_EXTENSION` | one release ∥ one modify on distinct scopes; no cross-talk | `PEER:.../runs/concurrent-a/`, `PEER:.../runs/concurrent-b/` | **PASS** (2 gates) | **NOT_RUN** |
| C11 | PFCP `UNKNOWN` explicit reconcile (no 3GPP message; `CA_EXTENSION`) | — (no Node; Owner-private) | `POST /nsmf-upn-context/v1/reconcile` | `OWNER:src/smf/mas/common/mas-reconcile-sbi.c` (`decide`, `evaluate_upf_observation`) | `CA_EXTENSION` | binds SUPI/PSI/generation/step/corr/epoch/SEID/UPF; `UPF_OBSERVATION` digest+freshness or `OPERATOR_ASSERTED`; never sends PFCP; `CONFIRMED_PRESENT`/`UNRESOLVED` keep the block | `PEER:artifacts/acceptance/20261123-scheme-c-reconcile/runs/reconcile-deleted/{checks.json,reconcile-request.json,upf-session-info.json}`, `.../reconcile-present/checks.json` | **PASS** (`PFCP_UNKNOWN_EXPLICIT_RECONCILE`, real ac E2E, 1 distinct PFCP deletion transaction) | **NOT_RUN** |
| C12 | Concurrent normal Release ∥ targeted PFCP Deletion timeout (no 3GPP step; `CA_EXTENSION` fault injection) | — | — | Mock AMF `parallel` groups; SMF test seam `OPENAMSM_TEST_PFCP_DROP_DEL_RESP`; `OWNER:src/smf/pfcp-sm.c` | `CA_EXTENSION` | Session A completes and clears; Session B enters `UNKNOWN` and retains its own context/SEID/generation; A's success does not unblock B; B's failure does not stop A; 2 distinct PFCP deletion transactions | `PEER:artifacts/acceptance/20261123-scheme-c-reconcile/runs/concurrent-release-timeout/checks.json` | **PASS** (`CONCURRENT_RELEASE_VS_PFCP_TIMEOUT`) | **NOT_RUN** |
| C13 | Agent restart + explicit Owner-observation recovery (no 3GPP step; `CA_EXTENSION`) | — | `POST /nnwagent-admin/v1/release-recovery` | `OWNER:tools/nw-agent/server.py`, `orch_engine.py` (`recover_release`) | `CA_EXTENSION` | after restart, only `r-sc` may be resumed and only when Owner proves generation/txn + N1/N2 + PFCP `ACCEPTED`/`CONFIRMED_DELETED`; otherwise `BLOCKED` | `PEER:.../runs/reconcile-deleted/checks.json` (`agent_restarted true`, `status COMPLETED`), `PEER:.../runs/restart-*/checks.json` | **PASS** (`AGENT_RESTART_*` + explicit recovery) | **NOT_RUN** |

### 4.4 AMF-requested `ReleaseSMContext` — MAPPING ONLY

| # | 3GPP procedure / message (§clause) | CA-SL Procedure Node | MAS capability / operation | OpenAMSM source | Impl type | Success / failure / UNKNOWN | Evidence | Verdict (5GC) | Verdict (Skill) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | `Nsmf_PDUSession_ReleaseSMContext` (TS 23.502 §4.3.4.2 step 1c; TS 29.502 §5.2.2.4) — no NAS from the UE; AMF-initiated context release | r2→r6 with `entryKind=AMF_INITIATED`, `trigger∈{6,7}` (`CASL:examples/skills/release-pdu-session-mas/SKILL.md:22-31`) | would need `SSM.SIGNAL_UE_AN` **no-signal** branch (`ssm_ue.c:339-347`) | `OWNER:tools/nw-agent/server.py:928-951` — drives the **legacy** `RELEASE` OES plan with `trigger=6`, not Scheme C | `3GPP_NATIVE` ingress; current executor is legacy-plan | legacy path: `run_modify_or_release` → `terminate_assoc` on success; no Scheme C semantics, no ledger, no `OUTCOME_UNKNOWN` classification | none in this round (`PEER:.../evidence.md` row `NETWORK_REQUESTED_RELEASE_SM_CONTEXT` = **BLOCKED**, `env-openamsm#10`) | **BLOCKED** | **NOT_RUN** |
| D2 | AMF-triggered no-N1/N2 branch (`trigger` 6/7) (TS 23.502 §4.3.4.2 step 1c) | r3 no-signal proof | `SSM.SIGNAL_UE_AN{trigger=6}` → OK, no signalling | `OWNER:src/smf/mas/ssm/ssm_ue.c:339-347` | `CA_ADAPTER` | source-level exists, but **unreachable via Scheme C**: the Scheme C build path forces `trigger=UE_REQUESTED` (`ssm_ue.c:289-290`) and `_release_cleanup` hardcodes `"2"` (`orch_engine.py:948`) | none | **BLOCKED** (mapping only) | **NOT_RUN** |

### 4.5 SMF-initiated Release — MAPPING + GAP

| # | 3GPP procedure / message (§clause) | CA-SL Procedure Node | MAS capability / operation | OpenAMSM source | Impl type | Success / failure / UNKNOWN | Evidence | Verdict (5GC) | Verdict (Skill) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | SMF-initiated PDU Session Release (internal trigger; `repo-cited, unverified`: `OWNER:src/smf/gsm-sm.c:3365` cites "TS 23.502 Section 4.3.4.3") | r2→r6 with `entryKind=NETWORK_TRIGGERED`, `trigger=5` | would need `trigger=SMF_INITIATED` (5) | **no Scheme C entry exists**: no SBI route, no internal event hook that reaches `run_c_release_request`; `ssm_ue.c:289-290` forces trigger 2; `_release_cleanup` forces `"2"` | — (gap) | n/a | none | **NOT_RUN** (no gate; gap) | **NOT_RUN** |
| E2 | Operator/explicit recovery as the only current substitute | — | `POST /nnwagent-admin/v1/release-recovery` | `OWNER:tools/nw-agent/server.py`, `orch_engine.py` (`recover_release`) | `CA_EXTENSION` | resumes only `r-sc`; refuses when pre-confirmation is incomplete, generation/txn mismatch, PFCP not `ACCEPTED`, or reconcile `UNRESOLVED`/`CONFIRMED_PRESENT`; `409` otherwise | `PEER:.../runs/reconcile-deleted/checks.json` (`recovery_status 200`, `status COMPLETED`) | **PASS** for the proven resume scope | **NOT_RUN** |

### 4.6 Verdict roll-up (verbatim from the evidence artifact)

From `PEER:artifacts/acceptance/20261122-scheme-c-release-reliability/evidence.md:7-25`:

| Gate | Verdict |
| --- | --- |
| `SCHEME_C_UE_MODIFY_POSITIVE` | PASS |
| `SCHEME_C_RELAY_FAIL_CLOSED` | PASS |
| `SCHEME_C_UE_RELEASE_POSITIVE` | PASS |
| `SCHEME_C_UE_RELEASE_ORDERING_AND_DUPLICATES` | PASS |
| `SCHEME_C_PFCP_DELETION_TIMEOUT` | PASS |
| `SCHEME_C_RELEASE_FINALIZE_FAILURE_INJECTION` | PASS |
| `CONCURRENT_ISOLATION_DIFFERENT_SUPI_SAME_PSI` | PASS |
| `CONCURRENT_ISOLATION_SAME_SUPI_DIFFERENT_PSI` | PASS |
| `AGENT_RESTART_AFTER_BUILD` | PASS |
| `AGENT_RESTART_BEFORE_CLEANUP` | PASS |
| `AGENT_RESTART_DURING_PFCP_DELETE` | PASS |
| `AGENT_RESTART_BEFORE_SC_FINALIZE` | PASS |
| `CONCURRENT_RELEASE_VS_PFCP_TIMEOUT` | NOT_RUN (single-UPF lab limitation) |
| `PFCP_UNKNOWN_EXPLICIT_RECONCILE` | **PASS** (2026-11-23, real ac E2E; §8.4) |
| `PFCP_UNKNOWN_RECONCILE_CONFIRMED_PRESENT` | **PASS** (context retained, no finalize) |
| `CONCURRENT_RELEASE_VS_PFCP_TIMEOUT` | **PASS** |
| `AGENT_RESTART_EXPLICIT_RECONCILE` | BLOCKED |
| `NETWORK_REQUESTED_RELEASE_SM_CONTEXT` | BLOCKED (`env-openamsm#10`) |
| `CA_AGENT_PROVIDER_SKILL_E2E` | NOT_RUN |

**Every row above is a 5GC/Owner-behaviour verdict. None of them is a CA-SL
Skill, Procedure, Runtime or Host verdict.** The CA-SL layer has no execution
evidence at all.

Also note the contradiction that must be resolved before promotion:
`CASL:docs/mas-lifecycle-acceptance-matrix.md:33` still states
"Release success … Runtime NOT_RUN" and `:28` claims a *development* E2E PASS
for Modify "on the isolated D5 stack (ca-agent-demo evidence)" — a different
stack from the one evidencing `SCHEME_C_UE_MODIFY_POSITIVE`. The CA-SL matrix is
therefore **stale** relative to `PEER` evidence, and the two must not be merged
into one verdict.

---

## 5. Legacy OES ordering vs current Scheme C ordering — explicit divergence

### 5.1 What the historical document says (must NOT be read as execution order)

`CASL:docs/mas-lifecycle-source-mapping.md:64-72` maps the pinned plan
`pdu-rel-v4.yaml` at `env-openamsm@594dec78` as:

| Historical node | Operation |
| --- | --- |
| r2 | `UPN.DELETE_UP_SESSION` |
| r3 | `SSM.SIGNAL_UE_AN` (release) |
| r4 | `PA.DELETE_SM_POLICY` |
| r5 | `SC.RELEASE_SM_CONTEXT` |
| r6 | `SE.EMIT_EVENTS` (`RELEASED`) |

The plan file confirms that static order (`OWNER:build/openamsm-source/tools/nw-agent/plans/release/pdu-rel-v4.yaml:16-66`:
r1 optional charging → r2 → r3 → r4 → r5 → r6 → r7 `COMPENSATE_RELEASE`).
`CASL:docs/mas-lifecycle-acceptance-matrix.md:11` repeats it as the Release
graph: `r2 -> r3 -> r4 -> r5 -> r6`.

**This is a plan-declaration order for a superseded execution path. It is not
the current Scheme C order and must not be cited as the actual runtime
sequence.**

### 5.2 What Scheme C actually does

Two structural differences, not merely a permutation:

1. **Signalling is moved before all destructive steps.** The UE-requested
   release sends the N1 Release Command + N2 Release Command first
   (`SSM` build), waits for **both** confirmations, and only then starts
   cleanup. In the historical plan, signalling (`r3`) sits *between* the UPN
   deletion (`r2`) and the PA deletion (`r4`).
2. **Cleanup order is changed** and is executed post-confirmation:

```
r-pa  PA.DELETE_SM_POLICY      {release=1, trigger=2}
r-upn UPN.DELETE_UP_SESSION    {trigger=2}
r-se  SE.EMIT_EVENTS           {ev=RELEASED}
r-sc  SC.RELEASE_SM_CONTEXT    {release=1, finalize=1, trigger=2}
```

Authoritative source: `OWNER:build/openamsm-source/tools/nw-agent/orch_engine.py:940-977`
(`_release_cleanup`, docstring: "after both N1 and N2 confirmations"), invoked
only from `run_c_release_confirm` (`orch_engine.py:1116`) once
`release_ready == "1"`.

**Standard-order deviation (explicit, not silent).** TS 23.502 §4.3.4.2 runs
the N4 Session Release (steps 2a/2b) **before** the N1 Release Command / N2
Resource Release (steps 3–5): the SMF releases the user plane and then asks the
UE/RAN to release the session. Scheme C sends the N1/N2 command first, waits
for **both** confirmations (`0xD4` and `PDU_RES_REL_RSP`), and only then runs
`r-pa → r-upn → r-se → r-sc`. This is a deliberate `CA_EXTENSION` ordering
deviation, adopted so that an unconfirmed UE/RAN release never destroys the
user plane prematurely and so that the single PFCP deletion is bound to a
confirmed generation/transaction.

Consequences, stated for review:

- The user-plane resources remain allocated until the UE/RAN confirm (longer
  than the normative order). The target PFCP session is still deleted exactly
  once, and only after both confirmations.
- The deviation does **not** authorize a retry, a second deletion, or a
  finalize without proof; the PFCP gate is unchanged.
- Product acceptance of this deviation is required before claiming normative
  step-order conformance. It is not an unexplained gap.

### 5.3 Divergence table

| Aspect | Historical OES `pdu-rel-v4` (594dec78) | Current Scheme C |
| --- | --- | --- |
| First destructive act | UPN delete (r2) | none until N1+N2 confirmed |
| Where signalling sits | r3, between r2 and r4 | before cleanup, as parse → build → 2 confirmations |
| UPN delete position | 1st | 2nd (`r-upn`) |
| PA delete position | 3rd (after signalling) | 1st (`r-pa`) |
| SE event position | last (r6) | 3rd (`r-se`), before SC |
| SC release position | 2nd-last (r5) | last (`r-sc`), with `finalize=1` clearing the context |
| Charging delete | optional r1 | absent |
| Compensation | r7 `COMPENSATE_RELEASE` | absent; failures stop and are classified `FAILED`/`UNKNOWN` |
| Trigger source | plan `from_start: trigger` (declared but undeclared input — source defect) | Agent hardcodes `2` |
| Context removal | `lifecycle=RELEASING` only, Host tombstones later | Owner clears the SM context when `finalize=1` + success + PFCP gate passes |

### 5.4 Runtime proof of the real order

`PEER:artifacts/acceptance/20261122-scheme-c-release-reliability/runs/normal/mas-trace.ndjson`
(excerpt, monotonic `t`):

```
… release_command_built
… release_n1_complete
… release_n2_complete
… PA -> PCF  DELETE_SM_POLICY   step=r-pa
… UPN -> PFCP DELETE_UP_SESSION step=r-upn
… NW-Agent -> SE EMIT_EVENTS    RELEASED
… SC -> UDM_UECM RELEASE_SM_CONTEXT step=r-sc
… NW-Agent -> SC ACK_AMF_RELEASE
```

The same `r-pa → r-upn → r-se → r-sc` chain is reproduced independently by the
fault-injection run (`PEER:.../runs/finalize-failure/checks.json` /
`mas-trace.ndjson`, `failedStep=r-sc`, `completedSteps=[r-pa,r-upn,r-se]`).

### 5.5 Required wording in any promoted document

> The `pdu-rel-v4` r2–r6 mapping is a **historical, plan-declaration-level**
> mapping pinned to `env-openamsm@594dec78`. It describes neither the current
> entry routing nor the current execution order. The current Scheme C release
> executes `SSM` parse → `SSM` build → `SSM` confirmation of N1 (`0xD4`) and N2
> (`PDU_RES_REL_RSP`), and only then `PA.DELETE_SM_POLICY →
> UPN.DELETE_UP_SESSION → SE.EMIT_EVENTS → SC.RELEASE_SM_CONTEXT(finalize)`.
> Any consumer that relies on r2–r6 as the runtime sequence is incorrect.

---

## 6. SKILL entry-semantics table

Entry semantics must stay distinct. In particular **UE Release is not an
"UpdateSMContext release operation"**: the standard entry operation is
`Nsmf_PDUSession_UpdateSMContext`, and the release semantics live in the NAS
payload.

| # | Entry semantics | Standard entry operation | Transport entry (current scheme) | Discriminator | Current implementation | Round status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **UE Establish** | `Nsmf_PDUSession_CreateSMContext` | `POST /nsmf-pdusession/v1/sm-contexts` | N1 5GSM Establishment Request (EPD `0x2E`) | `server.py:744-780`, plan `ESTABLISH_POLICY_FIRST` | implemented; not re-verified this round |
| 2 | **UE Modify** | `Nsmf_PDUSession_UpdateSMContext` | `POST …/sm-contexts/{ref}/modify` | NAS PDU Session Modification Request `0xC9` (201) | `server.py:873-880` → `run_c_modify` | implemented + evidenced |
| 3 | **UE Release** | `Nsmf_PDUSession_UpdateSMContext` (**same** operation as Modify) | `POST …/sm-contexts/{ref}/modify` | NAS PDU Session Release Request `0xD1` (209) | `server.py:829-846` → `run_c_release_request`; confirmations `0xD4`/`PDU_RES_REL_RSP` on the same path | implemented + evidenced |
| 4 | **AMF Context Release** | `Nsmf_PDUSession_ReleaseSMContext` | `POST …/sm-contexts/{ref}/release` | no NAS; AMF-originated, no N1/N2 to the UE | **MAP ONLY** — the route only drives the legacy `RELEASE` OES plan with `trigger=6` (`server.py:928-951`); not converged onto Scheme C | not implemented this round (`env-openamsm#10`) |
| 5 | **SMF-initiated Release** | *(no SBI operation — internal logical-SMF trigger)* | *(none)* | internal trigger, `trigger=5` per the pinned constant table | **MAP + GAP ONLY** — no entry exists; Scheme C forces `trigger=2` (`ssm_ue.c:289-290`, `orch_engine.py:948`) | not implemented this round |

Consequences for the Skills (must be reflected in any promoted Skill text):

- Rows 2 and 3 share one standard entry operation. A Skill must therefore
  discriminate on the NAS message type, not on the SBI operation name, and must
  never treat the SBI operation as proof of release semantics.
- Row 3 must not be described as "the release operation of Nsmf_PDUSession".
- Rows 4 and 5 must not be authored as executable Procedures until an entry
  exists; they stay mapping/gap rows.
- Continuations (`0xD4`, N2 `PDU_RES_REL_RSP`, N2 `PDU_RES_MOD_RSP`) are **not**
  entries and must never open a new Run (`CASL:docs/mas-lifecycle-owner-contract.md:74-80`).

---

## 7. Static regression check proposal (5GC-profile Skills only)

Scope: the 5GC-profile Skill packages only —
`CASL:examples/skills/establish-pdu-session-mas/`,
`CASL:examples/skills/modify-pdu-session-mas/`,
`CASL:examples/skills/release-pdu-session-mas/`, `CASL:skills/establish-pdu-session-mas/`.
A stand-alone read-only linter (proposal: `ca-skills/tools/check-5gc-profile-skills.*`
plus one CI step) over existing package files.

**Explicitly out of scope:** no change to CA-SL v1alpha5 grammar, no change to
the Compiler, no new schema combinators, no new language keywords. The checks
are *assertions about authored content*, not language features.

| # | Check | Assertion | Failure mode |
| --- | --- | --- | --- |
| S1 | Entry Service Operation present | Exactly one of the five entry semantics is declared, with its exact standard operation name (`CreateSMContext` / `UpdateSMContext` / `ReleaseSMContext` / internal trigger / none). `UpdateSMContext` must be qualified by the NAS message type. | missing / ambiguous / unknown operation name |
| S2 | Message ↔ trigger consistency | The declared NAS type must match the semantics: `0xC9` ⇒ Modify only; `0xD1` ⇒ UE Release only; `0xD4` and `PDU_RES_REL_RSP` / `PDU_RES_MOD_RSP` ⇒ continuations, never entries. Trigger codes must match the pinned table (`2/6/7/1/3/4/5`). | contradiction between declared entry and NAS type, or a continuation declared as an entry |
| S3 | MAS capability traceable | Every `mas::<MAS>.<OP>` node resolves to (a) a catalog op in `mas-types.h` + `catalog.c`, and (b) a real invoke function in `src/smf/mas/**`. Unresolvable node ⇒ fail. | invented/deprecated capability, or an op with no source locator |
| S4 | Standard vs extension distinguished | Each node carries an `implementation-type` annotation; `CA_EXTENSION` items (QueryContext, PFCP reconcile, `release-recovery`, `finalize`, tombstones, idempotency) must be labelled non-3GPP and must not be presented as a 3GPP step. | extension presented as standard procedure, or missing annotation |
| S5 | No stale references | The `594dec78` / `pdu-mod-v3` / `pdu-rel-v4` mapping must be labelled `HISTORICAL` and must not be cited as current execution order; no reference to files that do not exist; repeated execution-order claims must agree with §5.2. | stale pin cited as current; ordering claim contradicting `_release_cleanup` |
| S6 | Build identity matches evidence | Every `PASS` citation must carry the Owner `build_patch_identity` (or commit + patch list) and match the identity of the evidence set that produced it; a mismatch downgrades the claim to `STALE`, never `PASS`. Known identity defects (§0.2) must fail the check until corrected. | PASS without identity, or identity mismatch |

Exit semantics: S1–S4 are errors; S5–S6 are errors for any `PASS`/`VERIFIED`
claim, warnings otherwise. The linter must never emit `PASS` on its own — it can
only reject or stay silent.

---

## 8. Known gaps and limitations

### 8.1 Not implemented in this round

1. **Network-requested / AMF-requested `ReleaseSMContext`** — no Scheme C entry.
   The `/release` route exists but still executes the legacy OES plan with
   `trigger=6` (`server.py:928-951`). Tracked as `env-openamsm#10`; evidence gate
   `NETWORK_REQUESTED_RELEASE_SM_CONTEXT` = **BLOCKED**.
2. **SMF-initiated release** — no entry at all (no SBI, no internal hook). The
   source-level no-signal branch (`ssm_ue.c:339-347`) is unreachable through
   Scheme C because the build path forces `trigger=UE_REQUESTED`
   (`ssm_ue.c:289-290`) and cleanup hardcodes `"2"` (`orch_engine.py:948`).
   Consequence: even if an AMF/SMF entry were added, the trigger would have to be
   threaded through build **and** cleanup before the no-signal branch could ever
   execute.
3. **No CA-SL Skill/Runtime execution.** `CA_AGENT_PROVIDER_SKILL_E2E` =
   **NOT_RUN**; the Skills stay `NOT_LINKABLE / NOT_QUALIFIED` (no published
   ToolCatalog, no Owner receipts, no Evidence Guarantees).

### 8.2 Durability and recovery

4. **`after_build` restart is unrecoverable.** The N1/N2 command bytes left the
   Owner only in the lost HTTP response; the Owner's
   `release_in_progress`/`command_built` flags are sticky. A retry is refused
   (`409 OUTCOME_UNKNOWN`), the session stays until an explicit operator/native
   reconcile.
   Evidence: `PEER:.../runs/restart-after_build/checks.json`
   (`retry_status 409`, `retry_no_command true`, `context_retained true`,
   `owner_ssm.releaseCommandBuilt true`, `releaseN1Complete false`).
5. **Bounded, explicit Agent recovery.** The association cursor is still
   memory-only (no new database). A restarted Agent answers release-shaped
   requests `409 OUTCOME_UNKNOWN` and never replays. The supported recovery is
   an explicit operator call (`POST /nnwagent-admin/v1/release-recovery`) that
   reads Owner QueryContext and may resume **only** `r-sc` after generation/txn
   and N1+N2 confirmation are proven and PFCP is `ACCEPTED` or
   `CONFIRMED_DELETED`. `after_build` / `before_cleanup` stay `BLOCKED`.
6. **PFCP `UNKNOWN` explicit reconcile is implemented and proven on the real
   ac stack** (§8.4). `CONFIRMED_PRESENT` and `UNRESOLVED` keep every block.
7. **State retention is bounded, but the evidence narrative contradicts the
   code.** `PEER:…/20261122-…/evidence.md:237-239` states "the Agent never
   terminates a completed assoc (unbounded memory growth)". The current tree
   does the opposite: `run_c_release_confirm` calls
   `terminate_assoc(..., outcome="COMPLETED")`
   (`orch_engine.py:1135`), which moves the entry to a **bounded** tombstone
   (`ASSOC_TOMBSTONE_MAX = 512`, `ASSOC_MAX_ACTIVE = 4096`,
   `orch_engine.py:33-34, 563-565`), and `sweep_assocs()` runs on every business
   entry (`server.py:1004`). Treat the evidence sentence as **stale** and
   re-verify before quoting either version. Remaining true limitation: the
   Owner idempotency cache is process-local.

### 8.3 Semantics that must not be over-read

8. `APPLIED` for the QoS delta means PFCP QER accepted + N1/N2 dispatched. It is
   **not** RAN/UE acceptance; `RAN_MODIFICATION_CONFIRMED` /
   `TARGET_STATE_VERIFIED` require an independent observation
   (`CASL:docs/mas-lifecycle-owner-contract.md:76-85`).
9. `SE.EMIT_EVENTS(RELEASED)` is an in-memory marker — not a durable event, not
   a 3GPP SM Context Status Notify.
10. `SC.RELEASE_SM_CONTEXT` reports `lifecycle=RELEASING`; the context removal is
    a separate Owner-side `finalize` action gated on success + PFCP state, not
    an output field of the MAS operation.
11. A raw HTTP 2xx / `MAS status=OK` / local flag is not a commit receipt
    (`CASL:docs/mas-lifecycle-owner-contract.md:38`).

### 8.4 PFCP reconcile evidence — `UPF_OBSERVATION` vs `OPERATOR_ASSERTED`

The Owner keeps the evidence source explicit and never collapses the two
(`OWNER:src/smf/mas/common/mas-reconcile-sbi.c`, `decide()` and
`evaluate_upf_observation()`):

| Evidence source | How it is accepted | Trust level |
| --- | --- | --- |
| `UPF_OBSERVATION` | raw UPF `/session-info` listing + `sha256` + `observedAtUnix` within 300 s; the Owner re-hashes the exact bytes and looks up the target `upf_n4_seid` itself | machine observation of the UPF |
| `OPERATOR_ASSERTED` | operator + reason + `asserted=DELETED|PRESENT` | human assertion; **never** reported as an observation |
| `NONE` | records `UNRESOLVED`, keeps the gate closed | no evidence |

Real ac-stack E2E on the final build (Mock AMF → SCP → NW-Agent → real SMF/UPF;
one Session Deletion answer dropped for exactly the target SUPI/PSI; the PFCP
request is real and the SMF reaches its real timeout path):

- `PEER:artifacts/acceptance/20261123-scheme-c-reconcile/runs/reconcile-deleted/checks.json`
  — `CONFIRMED_DELETED`, `finalizeUnblocked=true`, `autoDelete=false`,
  `pfcpDeleteState` still `UNKNOWN`, exactly **1** distinct PFCP Session
  Deletion transaction; wrong generation / wrong SEID / cross-PSI / stale
  observation / bad digest / missing operator are all refused; NW-Agent is
  restarted before recovery; recovery returns `COMPLETED`; Owner session gone.
- `.../runs/reconcile-present/checks.json` — the real UPF still holds the target
  session (deletion sent with a deliberately wrong SEID, answer lost);
  `CONFIRMED_PRESENT`, `finalizeUnblocked=false`; recovery is refused
  (`409 PFCP_UNRESOLVED`); the context is retained.
- Late/duplicate transaction guard: after any reconcile decision, a stale PFCP
  deletion response is not claimable and cannot clear the context
  (`OWNER:src/smf/pfcp-sm.c`, post-complete `mas_upnode_pfcp_reconciled()`
  guard; `mas_upnode_pfcp_del_lifecycle_held()` also blocks UPF restoration).

Reconcile never sends PFCP and never removes a context. A second destructive
operation stays impossible: the retry predicate still sees `UNKNOWN`.

### 8.5 Traceability defects to fix before promotion

12. `build-identity.json` `source.tree_sha256` equals the pristine import digest
    (§0.2) — cannot identify the patched build.
13. The 2026-11-23 reconcile evidence set is committed with `build-identity.json`,
    `run-manifest.json` and `SHA256SUMS`; cite its `build_patch_identity`, not
    the pristine `source.tree_sha256`.
14. `CASL:docs/mas-lifecycle-acceptance-matrix.md` is stale versus `PEER`
    evidence (§4.6) and mixes two different stacks' PASS claims.
15. The historical mapping's "source-plan defect" (`start_inputs: {}` while
    r2/r3 reference `trigger`) no longer blocks anything in Scheme C, because
    Scheme C does not use that plan for UE-requested release. Keep it as a
    historical note; do not present it as a live blocker for §4.3.
16. `PEER:…/evidence.md` "Remaining limitations" still describes unbounded
    association retention, which the current tree contradicts (§8.2 item 7).
    Re-check and correct before quoting.

---

## 9. Evidence index (stable locators only)

| Purpose | Locator |
| --- | --- |
| Gate verdict table, build identity, topology | `PEER:artifacts/acceptance/20261122-scheme-c-release-reliability/evidence.md` |
| Build identity JSON | `PEER:…/20261122-…/build-identity.json` |
| Patch snapshots used by that run | `PEER:…/20261122-…/patches/0015…0019` + `SHA256SUMS` |
| Release positive (real N1/N2/PFCP) | `PEER:…/20261122-…/runs/normal/` (`mas-trace.ndjson`, `mock-amf.log`, `pfcp.pcap`, `run-manifest.json`) |
| Ordering / duplicate negatives | `PEER:…/20261122-…/runs/negative/` |
| PFCP deletion timeout | `PEER:…/20261122-…/runs/timeout/` |
| Finalize failure (real UDM UECM failure) | `PEER:…/20261122-…/runs/finalize-failure/` (`checks.json`, `mas-trace.ndjson`) |
| Restart points (4) | `PEER:…/20261122-…/runs/restart-{after_build,before_cleanup,during_cleanup_pfcp,before_sc_finalize}/checks.json` |
| Concurrency isolation | `PEER:…/20261122-…/runs/concurrent-a/`, `…/concurrent-b/` |
| Modify relay accept/reject/hang | `PEER:…/20261122-…/runs/relay-{accept,reject,hang}/` |
| Unit suites | `PEER:…/20261122-…/unit-tests/{python-unit-tests.log,c-unit-suites.log}` |
| Reconcile attempt (**FAIL**) | `PEER:artifacts/acceptance/20261123-scheme-c-reconcile/runs/reconcile-deleted/{checks.json,reconcile-request.json}` |
| Historical CA-SL mapping (HISTORICAL) | `CASL:docs/mas-lifecycle-source-mapping.md` |
| Owner outcome contract | `CASL:docs/mas-lifecycle-owner-contract.md` |
| CA-SL acceptance matrix (STALE) | `CASL:docs/mas-lifecycle-acceptance-matrix.md` |
| Release Skill | `CASL:examples/skills/release-pdu-session-mas/` (`SKILL.md`, `assurance/procedure.yaml`, `references/openamsm-operation-mapping.md`) |
| Modify Skill | `CASL:examples/skills/modify-pdu-session-mas/` |
| Establishment Skill | `CASL:examples/skills/establish-pdu-session-mas/`, `CASL:skills/establish-pdu-session-mas/` |
| Owner release orchestration | `OWNER:build/openamsm-source/tools/nw-agent/orch_engine.py:940-1136` |
| Owner entry routing | `OWNER:build/openamsm-source/tools/nw-agent/server.py:532-600`, `:744-960`, `:1050-1075` |
| Owner MAS sources | `OWNER:build/openamsm-source/src/smf/mas/{ssm,upn,pa,sc,se,common}/` |
| Owner patches (canonical diff) | `OWNER:patches/openamsm/0011…0021` |

---

## 10. Open items for the reviewer

1. Fill every `§clause` field in §4 from spec text, or accept the document as
   code-anchored only (recommended until a spec-text pipeline exists).
2. Decide whether the vertical slice is described as
   "UE-requested Release via UpdateSMContext + `0xD1`" (correct) or left as
   "Nsmf Release" (incorrect).
3. Fix or withdraw `build-identity.json:source.tree_sha256` before any consumer
   keys on it.
4. Re-run the reconcile scenario with the required body fields
   (`masStepId`, `masCorrId`, `n4Seid`, `upfId`, `sessionGeneration`) on a build
   with a recorded identity; only then can §8.4 move off FAIL.
5. Refresh `CASL:docs/mas-lifecycle-acceptance-matrix.md` so it stops claiming a
   different stack's PASS and stops reporting Release as NOT_RUN when Owner-level
   evidence exists — while keeping the Skill-level verdict NOT_RUN.
6. Decide whether the `trigger` hardcoding (`orch_engine.py:948`,
   `ssm_ue.c:289-290`) is an accepted Scheme C restriction or a defect to fix
   before AMF/SMF entries are added.

---

*End of draft. Nothing in this document asserts qualification, runtime
acceptance, or a merged release.*
