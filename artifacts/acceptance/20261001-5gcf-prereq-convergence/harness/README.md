# Validation harness (scratch-only, injected with `go test -overlay`)

These two Go test files are **not** part of the Toolchain repository and are not
part of the Skill package. They exist so the composition claim in this
acceptance record is reproducible without modifying `ca-skill-toolchain`.

Why a harness is needed at all: every production caller of `compiler.Compile`
(including `caskill compile` used by `make verify`) passes no
`DependencyResolver`, so a Skill that declares `spec.dependencies[]` fails closed
with `PR5_COMPOSITION_RESOLVER_UNAVAILABLE`. The harness supplies the missing
resolver so the shipped source can be validated against the real compiler.

## Reproduction

Prerequisites: `ca-skills` at the resolving commit, `ca-skill-toolchain` at
`2dadd40b2bb95d1072937f72c093d3e92f608738`, sibling `ca-runtime`,
`ca-sandbox`, `nodus` checkouts, and the Go caches described in the acceptance
README.

```bash
PLAT=/path/to/ca-skill-toolchain
HARNESS=/path/to/this/harness
WORK=$HOME/.cache/prereq7-harness            # scratch, never inside a repo
mkdir -p "$WORK"

cp "$PLAT/go.mod" "$WORK/workspace.mod"
cp "$PLAT/go.sum" "$WORK/workspace.sum"
cat >> "$WORK/workspace.mod" <<EOF

replace github.com/odango-chan/ca-runtime => /path/to/ca-runtime
replace github.com/odango-chan/ca-sandbox => /path/to/ca-sandbox
replace github.com/odango-chan/nodus => /path/to/nodus
EOF

cat > "$WORK/overlay-resolver.json" <<EOF
{"Replace": {"$PLAT/backend/internal/compiler/zz_prereq7_harness_test.go": "$HARNESS/resolver_harness_test.go"}}
EOF
cat > "$WORK/overlay-template.json" <<EOF
{"Replace": {"$PLAT/backend/internal/proceduretemplate/zz_prereq7_harness_test.go": "$HARNESS/template_harness_test.go"}}
EOF

export GOCACHE=/path/to/gocache GOMODCACHE=/path/to/gomodcache
export GOWORK=off GOFLAGS="-mod=mod -modfile=$WORK/workspace.mod"
export CA_BENCHMARKS_QUALIFICATION_DIR=/path/to/ca-benchmarks/qualification
export CA_SKILLS_ROOT=/path/to/ca-skills

cd "$PLAT"
# 1. real compiler with a digest-verifying resolver -> expect VALID
go test -overlay="$WORK/overlay-resolver.json" \
  ./backend/internal/compiler -run '^TestPrereq7Harness$' -count=1 -v

# 2. production Artifact ProcedureTemplate build -> expect PROCEDURE_TEMPLATE_UNSUPPORTED
go test -overlay="$WORK/overlay-template.json" \
  ./backend/internal/proceduretemplate -run '^TestPrereq7TemplateHarness$' -count=1 -v
```

## Observed results at the resolving commit

```text
TestPrereq7Harness        PASS  STATUS=VALID
  packageDigest       sha256:e5ce145e9b105b0d41d637234de6eb88fab2962583f124e3785485ce68ede87b
  caseSetDigest       sha256:c8a278aa19b0bf4ddb4f448553b0ea6c9c28824454cd10fb084f65fb62f93a10
  runtimeBundleDigest sha256:27aabc2930d36f4ffa44809a84ae1617084f96f2b66fe38035597afd4bbcbc17

TestPrereq7TemplateHarness PASS
  TEMPLATE procedure=prepare-file-transfer-normal ERROR=PROCEDURE_TEMPLATE_UNSUPPORTED:
    loop body node converge-receiver-registrations-ensure-registration-verify-current-registration must be action
  TEMPLATE procedure=prepare-file-transfer-urgent ERROR=PROCEDURE_TEMPLATE_UNSUPPORTED: (same)
  TEMPLATE procedure=release-virtual-group ERROR=PROCEDURE_TEMPLATE_INVALID:
    ToolResolver is required for Action procedure release-virtual-group   (harness-only: nil resolver)
```

The `release-virtual-group` line is an artifact of the harness passing nil
Tool/Script resolvers; it is not a finding about the Skill.

## Scope of the claim

`TestPrereq7Harness PASS` is **source/build evidence only**. It proves the
composition shape, digest binding, capability closure, budget partition, graph
lowering and all 17 cases are accepted by the real compiler once a resolver
exists. It is not `make verify` PASS, not a production Artifact, and not live
qualification.
