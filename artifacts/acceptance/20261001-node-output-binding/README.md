# Acceptance: 5gc-file-transfer virtual-group id via producing-node output (`ca-skills#13`)

- Scope: `odango-chan/ca-skills#13` — remove the unsatisfiable
  `context.facts.virtual_group.id` Procedure input from `5gc-file-transfer` and
  bind the virtual-group id from the producing node's output.
- Related: `odango-chan/ca-skills#7` (composition convergence that introduced the
  shape), `odango-chan/ca-runtime#116` (RUNTIME_ENGINE_PROCEDURE_BINDING_MISSING),
  `odango-chan/ca-benchmark-engine#38` (canonical E00 RUNTIME_ONLY run 2).
- Branch: `codex/5gcf-node-output-binding` (local only; not pushed, no PR).
- ca-skills base: `662d120c9eba6dd8e17c97e87323a84ff52237ee` (`origin/main`).
- Toolchain under test: `/Users/xiaotuanzi/ConnectionAgent/ca-skill-toolchain`
  at `eec53fcc6501b93bf264a47ec485fac01bf98e63` (clean; no toolchain change).
- Runtime for context only: `/Users/xiaotuanzi/ConnectionAgent/ca-runtime` at
  `406fe9af3df450c36bd03783e7354e207f459b13`.
- Environment: macOS, workspace-write.
  `GOCACHE=/Users/xiaotuanzi/ConnectionAgent/.agent-tmp/gocache`,
  `GOMODCACHE=/Users/xiaotuanzi/ConnectionAgent/.agent-tmp/gomodcache`,
  `TMPDIR=/Users/xiaotuanzi/ConnectionAgent/.agent-tmp/tmp`.

## Root cause

The Runtime freezes every declared `context.facts.*` Procedure input at
Procedure binding time from a deployment trusted-context resolver. No resolver
owns `facts.virtual_group.id` — it is produced during the run by
`create-vg` (`virtual_group.create`) or `reconcile-vg-create`
(`virtual_group.reconcile_create`). Declaring it as an input therefore failed
closed with:

```text
RUNTIME_HOST_INVALID_RESOLUTION: capability ProcedureTemplate binding: input
virtual-group-id: RUNTIME_ENGINE_PROCEDURE_BINDING_MISSING: facts.virtual_group.id
```

## Shape before -> after

Before (both `prepare-file-transfer-normal` and `prepare-file-transfer-urgent`):

```text
inputs.virtual-group-id: {type: string, from: context.facts.virtual_group.id}   # unsatisfiable
create-vg            --COMMITTED--> assign-members              groupId <- input.virtual-group-id
reconcile-vg-create  --COMMITTED--> assign-members              groupId <- input.virtual-group-id
assign-members       --OUTCOME_UNKNOWN--> reconcile-vg-members  groupId <- input.virtual-group-id
reconcile-vg-members --NOT_COMMITTED--> assign-members
```

`assign-members`/`reconcile-vg-members` each had two producing predecessors
(`create-vg` and `reconcile-vg-create`), so a single node-output binding could
not describe both, and the reconcile lineage must not trust an output whose
create returned `OUTCOME_UNKNOWN`.

After — convergence split per producing predecessor; every consumer has exactly
one producer for `groupId`:

```text
create-vg            --COMMITTED--> assign-members-after-create
                                       groupId <- create-vg.output.groupId
reconcile-vg-create  --COMMITTED--> assign-members-after-reconcile-create
                                       groupId <- reconcile-vg-create.output.groupId

assign-members-after-create
  --OUTCOME_UNKNOWN--> reconcile-vg-members-after-create
                         groupId <- create-vg.output.groupId
  --NOT_COMMITTED--> failed
assign-members-after-reconcile-create
  --OUTCOME_UNKNOWN--> reconcile-vg-members-after-reconcile-create
                         groupId <- reconcile-vg-create.output.groupId
  --NOT_COMMITTED--> failed

reconcile-vg-members-after-create
  --NOT_COMMITTED--> assign-members-after-create            # bounded retry preserved
reconcile-vg-members-after-reconcile-create
  --NOT_COMMITTED--> assign-members-after-reconcile-create  # bounded retry preserved

# terminal routing unchanged:
#   normal: COMMITTED -> verify-goal ; urgent: COMMITTED -> qos-boost -> verify-goal
#   reconcile UNRESOLVED -> unresolved ; reconcile FAILED/DENIED -> safe-stopped
```

The urgent path keeps the distinct `qos-boost` / `reconcile-qos` step; only the
group-id provenance and convergence split changed. No new syntax and no
toolchain change: the split uses existing `call`/`on` nodes and the already
grammar-legal `<node-id>.output.<path>` binding
(`schemas/v1alpha1/procedure-source.schema.yaml`).

## Files changed

```text
skills/5gc-file-transfer/assurance/procedure.yaml
  - removed inputs.virtual-group-id (from context.facts.virtual_group.id) in both procedures
  - replaced assign-members/reconcile-vg-members with per-predecessor siblings
    bound to create-vg.output.groupId / reconcile-vg-create.output.groupId
skills/5gc-file-transfer/cases/01..17
  - fixture key assign-members -> assign-members-after-create (or
    assign-members-after-reconcile-create for the reconcile-create lineage)
  - removed the now-unused facts.virtual_group.id context fact (facts: {})
skills/5gc-file-transfer/cases/18-node-output-binding-no-fact/  (new)
  - happy-path case with facts: {} proving the group id comes from node output
skills/5gc-file-transfer/SKILL.md
  - boundary: on prepare_transfer the group id is produced during execution, not a planning input
scripts/verify.py
  - focused hygiene assertion: run-produced fact ids (virtual_group.id) must not be
    bound as `from: context.facts.*` in an official Procedure source
```

## Exact commands and results

### Full gate — PASS

```bash
cd /Users/xiaotuanzi/ConnectionAgent/ca-skills/.agent-tmp/fact-binding
GOCACHE=/Users/xiaotuanzi/ConnectionAgent/.agent-tmp/gocache \
GOMODCACHE=/Users/xiaotuanzi/ConnectionAgent/.agent-tmp/gomodcache \
CA_SKILL_TOOLCHAIN_ROOT=/Users/xiaotuanzi/ConnectionAgent/ca-skill-toolchain \
make verify
# exit 0 ; "Skills verification: PASS"
# "COMPILE PASS | CASE PASS | PLANNING PASS | MOCK-RUNTIME PASS | ARTIFACT CONTRACT PASS"
# steps 1/8..8/8 all ok (see make-verify.log)
```

### Focused compile — PASS

```bash
python3 -B scripts/verify.py --compile skills/5gc-file-transfer
# PACKAGE_LAYOUT_OK ; status VALID ; findings []
```

New artifact digests (`focused-compile.txt`):

```text
packageDigest        sha256:e0456380cb37f1dee27d59f90d07c8700d9ba1ac4708be683212d810e7fd8958
sourcePackageDigest  sha256:e0456380cb37f1dee27d59f90d07c8700d9ba1ac4708be683212d810e7fd8958
runtimeBundleDigest  sha256:28e4dcadbd3442342dc93f0480924631b477608af96ae873c2b22f6a4eb5fbbf
caseSetDigest        sha256:be0440d72bbd97459ad61118a5189d4d7701195d534ffdfde54b1d2bb98dcf2a
registryDigest       sha256:18cea49c0f159ef7964357bab97ab4bed56f74729ec705639c921cda413da619
schemaDigest         sha256:31b0877d405b83b932b5997af3b5673f61a78679285c3dd9f98efb378ad6ed94
```

Digests are deterministic (verified by two consecutive focused compiles).

Baseline `origin/main` for comparison (`baseline-origin-main-compile.txt`):

```text
packageDigest        sha256:e5ce145e9b105b0d41d637234de6eb88fab2962583f124e3785485ce68ede87b
runtimeBundleDigest  sha256:27aabc2930d36f4ffa44809a84ae1617084f96f2b66fe38035597afd4bbcbc17
```

### Focused regression assertion — gates

The new hygiene assertion was exercised with a reversible negative fixture
(temporarily re-adding an `input` bound to `context.facts.virtual_group.id`),
then restored:

```bash
python3 -B scripts/verify.py --compile skills/5gc-file-transfer
# exit 1
# 5gc-file-transfer: Procedure input binds run-produced fact 'virtual_group.id'
#   from context.facts; bind it from the producing node's output instead
#   (odango-chan/ca-skills#13)
```

See `assertion-negative.txt`.

## Remaining gaps / not done

- `predicates.yaml` still scopes the `virtual_group.snapshot` observation with
  `facts["virtual_group.id"]` for `prepare_transfer`. That is a predicate-scope
  expression, not a Procedure input, so it is outside this fix and was not
  changed. It needs an owner decision: whether the Runtime resolves run-produced
  values in predicate scopes, or the observation scope must also stop relying on
  this fact. Tracked as a follow-up, not silently changed here.
- `wifi-file-transfer` has the same class of defect
  (`assurance/procedure.yaml` declares an input
  `from: context.facts.wifi_transfer.id`). Per scope it was **not** fixed here;
  it is a follow-up owner-issue candidate (see the commit/issue report).
- Local compile/case gates are not production qualification and were not run
  against live owners.
