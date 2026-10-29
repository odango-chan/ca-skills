# CreatedSession Toolchain consumer qualification

## Current revalidation (2026-10-29)

Current source heads:

- Skills: `c50681da11f8c8c070b4416c56131813149008c5`.
- Toolchain: `882ac439b8bd182213b06fc49be4389731269b30` (PR #132 candidate;
  owner `main` is not this candidate).
- Toolchain schema digest: `sha256:3fe530870dafe1f40f0031bfcd8118158c00dd0bcdc0ab9a9bd6d45bd99a6df2`.
- Child source package digest after native reconcile conversion:
  `sha256:cecc4a252ba33cbe91ca433ba0c35882d335992c30e9aa220194a24cdc096127`.

Results:

- Root `5gc-file-transfer` compile: PASS, `VALID`, zero findings.
- `make verify`: PASS, all eight repository gates and eight Python regressions.
- Child `establish-pdu-session` compile: INVALID with
  `PR5_VNEXT_RECONCILE_EFFECT_INVALID`: native reconcile requires its owning
  mutation to resolve to a registered mutation Capability. That owner contract
  is missing, so the compiler cannot qualify the recovery lineage or proceed to
  complete consumer validation. This replaces the older 19-finding result for
  the previous Skill source, which represented `reconcile` as a fake read-only
  Capability.
- Current logs: [child compile](establish-pdu-session-native-reconcile-compile.txt)
  and [repository verification](make-verify-current.txt).
- All four historical local script counterexamples remain covered by the
  eight regressions in `tests/test_createdsession_script_inputs.py`.

No Capability contracts were fabricated. Local Root compile and `make verify`
do not establish child qualification, production admission, or live acceptance.

## Scope

Rechecked the current `ca-skills` CreatedSession source candidate against the available local `ca-skill-toolchain` candidate. The Root `5gc-file-transfer` package and its Cases pass, while the child `establish-pdu-session` package that contains the four post-transfer Predicate refs still fails compile. This is Toolchain compile and Case evidence only; it is not production qualification or live 5GC acceptance.

## Historical exact inputs (revalidation before native reconcile conversion)

- Skill repository: `codex/createdsession-source-candidate` at `cdfd89da40da57c671a35aed9e8cc20813bac33e`.
- Toolchain checkout: `codex/createdsession-skill-local-predicates-128` at `9993c413dff7a897907ae7d228dc70606f023ad9`.
- Skill package digest: `sha256:0dbc8454ee2ee8933857664b2565b84df94245da53d53f04c0bf34b64ce621ca`.
- Runtime bundle digest: `sha256:8301891f569f0045c421347cf8a719d842dbd006031b3c61c4c5d049bf15f89b`.
- Case set digest: `sha256:2e67970855ccd37022800b1cb1a640e12962619d5f4234f6c74e18a8dde2730d`.
- Registry digest: `sha256:961b776567719a53be81a31ae3c4f105540449299c5113fbbb5cd0fdeb00d9db`.
- Schema digest: `sha256:d749d1ccf6165b15570733ceff4465e35c52ca52b73ca9391f31a55ee8842ef8`.

## Results

- `python3 -B scripts/verify.py --compile skills/5gc-file-transfer`: PASS; compile report `VALID`, zero findings.
- `make verify`: PASS; repository verifier reports `COMPILE PASS | CASE PASS | PLANNING PASS | MOCK-RUNTIME PASS | ARTIFACT CONTRACT PASS`; all 8 Python unit tests pass.
- Deterministic `planning-test`: PASS for all 17 committed CreatedSession Cases.
- `mock-run`: PASS for each of the 14 Cases with a selected Procedure. The three blocked-admission Cases have no selected Procedure and were exercised by `planning-test` only.
- For the explicit Case gates, `caskill` was invoked from the Toolchain checkout with the Skill package, registry, and relative case directory (`cases/<case>`). `mock-run` also received the Case's expected Procedure name.

The separate `establish-pdu-session` child package compile on the same exact commits returned `INVALID` with 19 `CAPABILITY_NOT_FOUND` findings and zero Predicate binding findings. Its 9 distinct unresolved Capability refs are:

- `sbi.udm.sm_data.get`
- `fivegc.session.operation_context.read`
- `sbi.udm.sdm_subscription.create`
- `sbi.pcf.sm_policy.create`
- `createdsession.operation.reconcile`
- `sbi.amf.n1n2.transfer`
- `fivegc.session.resource_responsibility.transfer`
- `fivegc.session.evidence.await`
- `fivegc.session.establishment_response.prepare`

Toolchain `AGENTS.md` assigns `CapabilityContract.v1` ownership to Runtime and limits Platform to build-time `CapabilityRequirement` reference validation. Runtime is read-only for this goal, so these findings cannot be fixed by inventing Skill or Reference Registry contracts. The exact compile command was `python3 -B scripts/verify.py --compile skills/establish-pdu-session` with the same `CA_SKILL_TOOLCHAIN_ROOT`; it exited 1 with the findings above.

| Case | Planning | Mock Runtime |
| --- | --- | --- |
| `01-normal-ready` | PASS | PASS |
| `02-goal-failed` | PASS | PASS |
| `03-create-unknown-committed` | PASS | PASS |
| `04-create-unknown-not-committed` | PASS | PASS |
| `05-create-unknown-unresolved` | PASS | PASS |
| `06-denied` | PASS | PASS |
| `07-budget-exhausted` | PASS | PASS |
| `08-budget-pending` | PASS | PASS |
| `09-resource-unavailable` | PASS | Not applicable; no Procedure selected |
| `10-urgent-ready` | PASS | PASS |
| `11-release-ready` | PASS | PASS |
| `12-registration-failed-admission-blocked` | PASS | Not applicable; no Procedure selected |
| `13-session-absent-created` | PASS | PASS |
| `14-baseline-qos-insufficient-converged` | PASS | PASS |
| `15-urgent-session-absent` | PASS | PASS |
| `17-registration-unknown-admission-blocked` | PASS | Not applicable; no Procedure selected |
| `18-node-output-binding-no-fact` | PASS | PASS |

The compiler report from `make verify` for the Root `5gc-file-transfer` package was `VALID` with the same package, runtime-bundle, Case-set, registry, and schema digests above. The full compiler JSON was emitted to stdout by `caskill`; no persistent report file was created by that command. The `make verify` gate does not compile the separate `establish-pdu-session` child package.

## Limits and remaining work

- The Toolchain candidate was not confirmed merged to its owner main branch during this run.
- Root compile/planning/mock gates do not establish formal release qualification or active production Capability Admission. The child Skill remains uncompiled because Runtime-owned Capability contracts are absent from the reference snapshot; Provider/Fabric cross-process operation, authoritative live Observations and protocol compatibility are also unverified.
- Fabric's authenticated, durable and operation-correlated `UpdateSMContext` source remains unresolved. Real UE/5GC acceptance was not run.
