# CreatedSession Toolchain consumer qualification

## Scope

Rechecked the current `ca-skills` CreatedSession source candidate against the available local `ca-skill-toolchain` candidate after earlier reports of `CAPABILITY_NOT_FOUND` findings. This is Toolchain compile and Case evidence only; it is not production qualification or live 5GC acceptance.

## Exact inputs

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

The compiler report from `make verify` was `VALID` with the same package, runtime-bundle, Case-set, registry, and schema digests above. The full compiler JSON was emitted to stdout by `caskill`; no persistent report file was created by that command.

## Limits and remaining work

- The Toolchain candidate was not confirmed merged to its owner main branch during this run.
- These compile, planning, and mock gates do not establish formal release qualification, active production Capability Admission, Runtime owner acceptance, Provider/Fabric cross-process operation, authoritative live Observations, or protocol compatibility.
- Fabric's authenticated, durable and operation-correlated `UpdateSMContext` source remains unresolved. Real UE/5GC acceptance was not run.
