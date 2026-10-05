# Acceptance: 5gc-file-transfer prerequisite convergence closure (`ca-skills#7`)

- Scope: `odango-chan/ca-skills#7` — close the business-prerequisite convergence
  gap so unregistered / session-absent / QoS-insufficient participants are
  converged instead of failing unconditionally.
- Classification against current `main`: **ALREADY_DONE** for the business
  source (merged as `ca-skills@cd4c0e6`, PR #11) plus one **NARROW_CODE_GAP**
  in the repository gate (`scripts/verify.py` still exported the retired
  `CA_SKILLS_ROOT` alias and `make verify` step 3/8 failed on current Toolchain
  main).
- Verified at `ca-skills@b3bb0b6` (current `origin/main`).

## Owner heads used for verification

```text
ca-skills            b3bb0b6c707d79317de8261a1d7327fdb190c50d
ca-skill-toolchain   4bd4ff7f8312b07051861712889bbeba7e19eb82
ca-benchmark-engine  d9009d727b34bbb67ed9fdebdb8fc0802ad07607
ca-benchmarks        c6f7c2954dc4ff9aa17196bb85bbb94e35284c04
ca-5gc-sim           b16e7d1272762890240f1aa799a37d9fd44acb56
ca-lab               99e176cd7e42dd6367bb1c89687a9371db01d654
ca-runtime           53c230fa72d4d9d3fb5a459768a3a2e41dfed39b
```

Reference E00 live evidence was produced at `ca-skills@b3bb0b6`, i.e. the same
tree verified here (see "Cross-repo live evidence").

## The code change in this acceptance

`scripts/verify.py` exported both `CONNECTIONAGENT_SKILLS_ROOT` and
`CA_SKILLS_ROOT` into the Toolchain gate environment. The Toolchain retired
those aliases and reads only the canonical `CA_SKILL_ROOT`
(`skilldependency.EnvOfficialSkillRoot`, commit
`ca-skill-toolchain@c9d9e3f`, #113). With the retired names exported,
`go test ./backend/internal/compiler -run ^TestCanonicalCaseRejectsSplitFilesAndUnknownFields$`
failed closed, so `make verify` could not pass.

```diff
-    env["CONNECTIONAGENT_SKILLS_ROOT"] = str(ROOT)
-    env["CA_SKILLS_ROOT"] = str(ROOT)
+    # Canonical official Skill checkout root read by the Toolchain
+    # (`skilldependency.EnvOfficialSkillRoot`). The legacy
+    # `CA_SKILLS_ROOT` / `CONNECTIONAGENT_SKILLS_ROOT` aliases were retired by
+    # odango-chan/ca-skill-toolchain#113; re-adding them here would be a
+    # compatibility shim the Toolchain no longer reads.
+    env["CA_SKILL_ROOT"] = str(ROOT)
```

Observed before the change:

```text
=== 3/8 canonical Case / authoring-model validation ===
--- FAIL: TestCanonicalCaseRejectsSplitFilesAndUnknownFields (0.00s)
    case_layout_test.go:11: CA_SKILL_ROOT is required for canonical Skill fixture tests
FAIL
Skills verification: FAIL (1)
```

## Gate commands and results

`GOCACHE` is pointed inside the workspace because this sandbox denies reads of
the default macOS `~/Library/Caches/go-build`; that is a sandbox-only workaround,
not a repository requirement.

```bash
cd ca-skills && GOCACHE="$PWD/.agent-tmp/gocache" make verify
```

Result: **PASS** — steps 1/8 through 8/8, `MAKE_VERIFY_EXIT=0`, ending with:

```text
Skills verification: PASS
COMPILE PASS | CASE PASS | PLANNING PASS | MOCK-RUNTIME PASS | ARTIFACT CONTRACT PASS
```

Raw log: `make-verify.log`.

Focused compile:

```bash
cd ca-skills && GOCACHE="$PWD/.agent-tmp/gocache" \
  python3 -B scripts/verify.py --compile skills/5gc-file-transfer
```

Result: **PASS**, `status: VALID`, `FOCUSED_EXIT=0`, with

```text
sourcePackageDigest sha256:8474f1bce28f3fed591320b085f35ce9297f69009841a2e39a1c2f46428d9453
runtimeBundleDigest sha256:57eb9e0565666ef9f90811eef1d4943eb407a0d9e7b9b983a87dbd92c81f17db
caseSetDigest       sha256:4b42ff363d64529a41dc44df92c3e5946d8428e99f05a4fb2b8201e369964a43
```

Raw log: `focused-compile.log`.

## Acceptance clause mapping

| # | Clause | State | Evidence |
| --- | --- | --- | --- |
| 1 | architecture-approved composition contract | DONE | `ca-skill-toolchain` `spec.dependencies[]` + `{skill,procedure,postcondition}` `procedure` node + `budgetPartition` (PR #116/`2dadd40`, #117/#118 closed); reference migration in `skills/5gc-file-transfer/assurance/contract.yaml`; #102 core landed, remaining items (composition ADR, Variant-selection enforcement) are explicitly non-blocking follow-ups |
| 2 | no unconditional failure on registration/session FAIL | DONE | `assurance/procedure.yaml` normal+urgent start with `converge-sender-registration` / `converge-receiver-registrations` / `converge-receiver-sessions`; `FAILED` is a business outcome after convergence |
| 3 | unregistered participants converged before transfer mutations | DONE | cases `12-unregistered-ue-converged`; live: E00 run `converge-sender-registration-*` nodes |
| 4 | missing PDU session converged before endpoint/VG work | DONE | `ensure-session-qos.observe-session-then-converge` composition; case `13-session-absent-created` |
| 5 | urgent path converges session/QoS, distinct boost | DONE | `prepare-file-transfer-urgent` composes the same prerequisites then `transfer.qos.boost`/`reconcile`; cases `14`, `15` |
| 6 | independent `file_transfer.request.satisfied` proof | DONE | `verify-goal` node on all three procedures; `assurance/predicates.yaml` single final predicate; live E00 `verify-goal PASS` |
| 7 | qualification adds non-ready starting-state cases | DONE | cases `12`–`17` (registration-absent, session-absent, QoS-insufficient, urgent session-absent, prerequisite DENIED fail-closed, UNKNOWN safe-stop) |
| 8 | `make verify` and focused compile pass | DONE | this artifact: `make verify` 8/8 PASS, focused compile VALID |
| 9 | Benchmark exercises variants without private Procedure nodes | DONE | E00 binds `capability:file_transfer.orchestrate` only; canonical RUNTIME_ONLY System Run PASS (below) |

## Cross-repo live evidence

Canonical E00 / RUNTIME_ONLY System Run:

- Locator: `ca-benchmark-engine:artifacts/acceptance/20261005-e00-owner-migration-system-run-pass/run-manifest.json`
  (`outcome: OK`) plus `run-manifest-second.json` (two consecutive PASS);
  commit `ca-benchmark-engine@a65605c`.
- `run-summary.json` records `ownerHeads.ca-skills.head = b3bb0b6c…` and the
  Runtime bundle `sourcePackageDigest = sha256:8474f1bce28f3fed591320b085f35ce9297f69009841a2e39a1c2f46428d9453`,
  which is byte-identical to the focused compile above.
- `runtime-run-events-host-run-82a48ee72818c63f754699f0` shows the composed
  convergence nodes executing (`converge-sender-registration-*`,
  `converge-receiver-registrations`, `converge-receiver-sessions`) with
  owner-native `fivegc-source-fact` evidence, then `resolve-member-endpoints`,
  `ensure-edge-cache`, `create-vg`, `assign-members`, and `verify-goal PASS`,
  ending `domainTerminal: SUCCEEDED`.
- The Benchmark references the Skill only by capability/entrypoint; it does not
  name any private Procedure node.

Environment/value owner chain for `networkPolicy`: `ca-lab#15` (closed),
`ca-5gc-sim#12` (closed, owner-local transfer/VG/QoS operations + facts),
`ca-sandbox#19` (closed, 5GC subtraction), `ca-runtime#124` (closed,
`internal/provider/fivegcsim` rebind), `ca-benchmark-engine#83` (closed, runner
wiring).

## Residual scope (not part of this issue)

- `ca-skill-toolchain#102` remains open only for explicitly non-blocking
  follow-ups (composition ADR, Variant-selection enforcement).
- model-live Benchmark branches remain blocked by `EXTERNAL_CREDENTIAL`
  (`ca-benchmark-engine:artifacts/acceptance/20261006-model-credential-preflight/run-manifest.json`),
  which is unrelated to this Skill's prerequisite convergence.
