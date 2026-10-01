# Acceptance: 5gc-file-transfer prerequisite convergence (`ca-skills#7`)

- Scope: `odango-chan/ca-skills#7` — real business prerequisite convergence for
  `5gc-file-transfer` via executable Skill composition.
- Composition contract: `odango-chan/ca-skill-toolchain#102` (merged as
  `ca-skill-toolchain@2dadd40`, PR #116).
- Branch: `codex/5gcf-transfer-prereq-convergence` (local only; not pushed, no PR).
- Environment: macOS, workspace-write. Go caches:
  `GOCACHE=/Users/xiaotuanzi/ConnectionAgent/.agent-tmp/gocache`,
  `GOMODCACHE=/Users/xiaotuanzi/ConnectionAgent/.agent-tmp/gomodcache`.
- Toolchain under test: `/Users/xiaotuanzi/ConnectionAgent/ca-skill-toolchain`
  at `2dadd40b2bb95d1072937f72c093d3e92f608738` (== `origin/main`).

## What changed

```text
skills/5gc-file-transfer/assurance/contract.yaml
  spec.dependencies[] = ue-registration, ensure-session-qos (artifactRef + digest)
  planning.maxActions 13 -> 174 with explicit budgetPartition {9, 165}
skills/5gc-file-transfer/assurance/procedure.yaml
  normal + urgent prepare paths now start with composed prerequisite convergence:
    converge-sender-registration  (top-level composition site, postcondition ue.registered)
    converge-receiver-registrations  (for over receiverImsis -> ue-registration)
    converge-receiver-sessions       (for over receiverImsis -> ensure-session-qos)
  virtual_group.create fiveQi now binds input.policy-five-qi
skills/5gc-file-transfer/assurance/predicates.yaml
  deleted transfer.participants.registered, transfer.participants.pdu_sessions_active
  (unbound ObservationRefs, hard-coded sst/sd); file_transfer.request.satisfied kept
skills/5gc-file-transfer/schemas/file-transfer-request.schema.yaml
  + request.networkPolicy {dnn, sst, sd, pduSessionId, fiveQi} required for prepare_transfer
skills/5gc-file-transfer/cases/01..10
  stale verify-registration/verify-sessions fixtures replaced; networkPolicy added
skills/5gc-file-transfer/cases/12..17
  new qualification cases (see below)
skills/5gc-file-transfer/SKILL.md
  thin semantics: convergence, networkPolicy ownership, baseline-vs-urgent QoS
docs/network-policy-identity.md
  canonical network policy contract (new)
```

## Composition shape

Dependencies are pinned by frozen source-package digest (see "Dependency digest
provenance"). Each top-level `procedure` composition site maps all four dependent
terminal outcomes (`SUCCEEDED/FAILED/UNRESOLVED/SAFE_STOPPED`). Per-participant
convergence uses `for` with a `procedure` body; the enclosing `for.on` routes the
dependent terminals.

Worked example of the compiled namespacing (from the real compiler, see
`composed-node-ids.txt`):

```text
converge-sender-registration
  -> converge-sender-registration-ensure-registration-verify-current-registration
  -> converge-sender-registration-ensure-registration-resolve-identity
  -> ... (inlined ue-registration graph)
  -> converge-sender-registration-ensure-registration-postcondition   (synthesized)
converge-receiver-registrations   (for, body = ue-registration.ensure-registration)
converge-receiver-sessions        (for, body = ensure-session-qos.observe-session-then-converge)
```

`ensure-session-qos.observe-session-then-converge` is chosen because it is the one
procedure that self-branches over the full baseline convergence state
(query -> absent => create, present+QoS-insufficient => modify, satisfied => verify),
so it covers the "absent session" and "insufficient baseline QoS" starting states
without duplicating any of that graph here.

## Policy contract

`request.networkPolicy = {dnn, sst, sd, pduSessionId, fiveQi}` is the single
canonical baseline value set. Shape owner = `ca-skills`; value owner = business
materialization / gateway (same pattern as `transferId`). Because
`odango-chan/ca-lab#15` is still open, the value has no Environment owner yet and
is therefore taken as an explicit request field supplied by business
materialization; the request schema fails closed when it is absent for
`prepare_transfer`.

All three consumers read the same object by binding:

```text
composed ensure-session-qos input  dnn,sst,sd,fiveqi  <- input.policy-*
virtual_group.create               fiveQi             <- input.policy-five-qi
baseline verification              dependent postconditions (pdu_session.*/user_plane.*)
```

Urgent acceleration stays the distinct `transfer.qos.boost`/`transfer.qos.reconcile`
path and never rewrites the baseline `fiveQi`. See `docs/network-policy-identity.md`.

## Dependency digest provenance

`artifactRef` + `digest` are the dependency package `sourcePackageDigest` values
produced by the repository's own focused compile for the same frozen source tree:

```bash
python3 -B scripts/verify.py --compile skills/ue-registration
#   "sourcePackageDigest": "sha256:8c82c4b7eaa901fb4ad4e532d7db84e332168916f42a5fb25333e379cf7fbdc1"
python3 -B scripts/verify.py --compile skills/ensure-session-qos
#   "sourcePackageDigest": "sha256:0d5f2157cdb08d23b989ff79461b7a731b6988b698cec916a28f72eb964f7d1e"
```

The compiler resolves `artifactRef` against the sibling `ca-skills` checkout,
re-hashes that package and fails closed on a missing/mismatched digest.

## Exact commands and results

### `make verify` — FAIL (blocked, step 6/8)

```bash
cd ca-skills && GOCACHE=.../gocache GOMODCACHE=.../gomodcache \
  CA_SKILL_TOOLCHAIN_ROOT=/Users/xiaotuanzi/ConnectionAgent/ca-skill-toolchain \
  make verify
# => MAKE_VERIFY_EXIT=2  ("Skills verification: FAIL (1)")
```

Steps 1-5 PASS (`ok .../backend/internal/compiler`, `.../planning`,
`.../mockruntime`). Step 6/8 `5gc-file-transfer compile` fails:

```text
PR5_COMPOSITION_RESOLVER_UNAVAILABLE  "dependency resolver is required for ue-registration"
PR5_COMPOSITION_RESOLVER_UNAVAILABLE  "dependency resolver is required for ensure-session-qos"
PR5_COMPOSITION_DEPENDENCY_NOT_DECLARED x6 (normal+urgent sites; consequence of the above)
```

### `python3 -B scripts/verify.py --compile skills/5gc-file-transfer` — FAIL

```text
PACKAGE_LAYOUT_OK
status: INVALID
PR5_COMPOSITION_RESOLVER_UNAVAILABLE x2
PR5_COMPOSITION_DEPENDENCY_NOT_DECLARED x6
FOCUSED_EXIT=1
```

### `python3 -B scripts/verify.py` — FAIL

Identical to `make verify`: steps 1-5 PASS, step 6/8 FAIL, `VERIFY_PY_EXIT=1`.

### Baseline control (unmodified `origin/main` package)

The same focused compile on the unmodified package PASSes, so the failure is
introduced by `spec.dependencies[]`, not by the environment:

```text
status: VALID   (sourcePackageDigest sha256:2415fb75...)
Focused compile: PASS (5gc-file-transfer)   EXIT=0
```

### Overlay compiler harness — PASS with a DependencyResolver supplied

Because no production caller wires a `DependencyResolver` (see Blockers), the
composed source was validated by injecting a filesystem resolver into the real
compiler with `go test -overlay`. The overlay does **not** modify the toolchain
checkout and does **not** change the shipped Skill source.

```bash
go test -overlay=<scratch>/overlay.json ./backend/internal/compiler \
  -run '^TestPrereq7Harness$' -count=1 -v
#   STATUS=VALID
#   packageDigest        sha256:e5ce145e9b105b0d41d637234de6eb88fab2962583f124e3785485ce68ede87b
#   caseSetDigest        sha256:c8a278aa19b0bf4ddb4f448553b0ea6c9c28824454cd10fb084f65fb62f93a10
#   runtimeBundleDigest  sha256:27aabc2930d36f4ffa44809a84ae1617084f96f2b66fe38035597afd4bbcbc17
```

`packageDigest`/`caseSetDigest` are computed over the discovered source bytes, so
they are identical to the digest the CLI reports for the same tree; only the
`status` differs (VALID with a resolver, INVALID without).

Read this as: the composition, lowering, capability closure, budget partition and
all 17 cases are accepted by the real compiler once a digest-verifying resolver
exists. It is **source/build evidence only**, not a substitute for the gate.

## Qualification cases

Coverage obligation `outcome_unknown_safe_stopped` is now satisfied, so the
composed package's platform-derived obligation set is fully covered.

| Case | Class | Starting state / intent |
| --- | --- | --- |
| 12-unregistered-ue-converged | happy_path | sender not registered -> converged then transfer prepared |
| 13-session-absent-created | session_create | receiver PDU session absent -> created and verified |
| 14-baseline-qos-insufficient-converged | session_modify | session present, baseline QoS insufficient -> modified |
| 15-urgent-session-absent | session_create | urgent path with session absent, urgent boost stays distinct |
| 16-prerequisite-denied-fails-closed | action_denied | identity resolve DENIED -> FAILED, no fake postcondition |
| 17-prerequisite-unknown-safe-stops | outcome_unknown_safe_stopped | authentication OUTCOME_UNKNOWN -> SAFE_STOPPED |

Cases 01-08/10 were updated: the deleted
`transfer.participants.*` fixtures were replaced with the composed
convergence-node fixtures, and `networkPolicy` was added to the requests.

## Blockers / gaps found (not fixed here; Toolchain-owned)

These are the reason the declared gates cannot pass. They are all in
`ca-skill-toolchain` and were left unmodified per the isolation rule.

1. **No production `DependencyResolver` (hard gate blocker).**
   `DependencyResolver` exists only in `backend/internal/compiler` and its unit
   tests. `service.Compile`, `caskill compile`, and every `compiler.Compile`
   caller (including the `make verify` step 6 and Mock-Runtime case gate) pass
   `nil`, so any `spec.dependencies[]` yields
   `PR5_COMPOSITION_RESOLVER_UNAVAILABLE` and then
   `PR5_COMPOSITION_DEPENDENCY_NOT_DECLARED`.
   Required: an owner-provided resolver that maps `artifactRef` to the frozen
   sibling source package and verifies the declared digest, wired into the CLI
   and the case/mock gates.

2. **Composed `for` bodies cannot be frozen into a ProcedureTemplate
   (production build blocker).** `proceduretemplate.Compile` requires every loop
   body node to be an `action` (`backend/internal/proceduretemplate/compiler.go`
   "loop body node ... must be action"), so the per-participant convergence
   cannot become a Runtime Artifact:

   ```text
   TEMPLATE procedure=prepare-file-transfer-normal
     ERROR=PROCEDURE_TEMPLATE_UNSUPPORTED: loop body node
     converge-receiver-registrations-ensure-registration-verify-current-registration
     must be action
   ```

3. **`for` is not executable/fixture-addressable by the Mock Runtime
   (qualification blocker).** The mock runtime has no loop support;
   `mockPathReachesVerify` has no `for` branch; `checkMockOutcomeKeys` /
   `checkMockPredicateKeys` and `graphFeatures` index only top-level nodes. So
   loop-body convergence steps cannot be pinned by case fixtures and their
   capability features (`has_create/modify/query`) are not derived. Cases 13-15
   therefore document the intended starting state and expect the converged
   terminal, but cannot pin per-iteration outcomes.

4. **`PR5_COMPOSITION_FOR_POSTCONDITION_UNSUPPORTED`.** A `for`-body composition
   site may not declare a `postcondition`, so only the sender site carries the
   synthesized authoritative re-verification. Receiver convergence relies on the
   dependent procedure's own terminal postcondition verification.

Per the task instruction, no bypass was hand-rolled. If (2) is considered
acceptable to leave open, (1) still blocks every declared gate.

## What remains / not done

- `make verify` is **not** PASS; no PASS claim is made. Steps 1-5 PASS, step 6/8
  fails on Toolchain wiring.
- No production Artifact/ProcedureTemplate was built (blocked by gap 2).
- Live owner execution / production qualification was not run.
- `networkPolicy` values still have no Environment owner until `ca-lab#15`.
