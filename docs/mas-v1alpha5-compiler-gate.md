# MAS Skill v1alpha5 — Compiler v2.0.0 gate

**State (2026-11-19): INPUT_BLOCKED / NOT_LINKABLE.** This is a reproducible compilation entrypoint and dependency inventory, **not** a claim of a successful formal Build or a published MAS Owner. Compiler v2.0.0 has been released: https://github.com/odango-chan/ca-skill-compiler/releases/tag/v2.0.0.

## Source of truth

Only `examples/skills/establish-pdu-session-mas/` from this repository is submitted to the v1alpha5 Compiler. The `ca-agent-demo/skills/establish-pdu-session-mas/` historical source and old `ca-skill-compiler/examples/ca-agent-demo-project/` are not current compiler inputs.

The official MAS example still contains a candidate `mas` dependency, 14 candidate Capability IDs, and 12 candidate Predicate result Schema IDs. These have no published trusted Owner export. Disabling validation, suppressing diagnostics or renaming placeholders cannot make a trustworthy Owner.

Compiler v2.0.0 consumes complete, immutable source plus resolved snapshots and trusted deployment bindings. It is not a package installer or Owner publisher.

## Reproducible compiler entrypoint

`scripts/compile_mas_v1alpha5.py` stages the official MAS Skill **without editing it**, copies only explicitly supplied trusted snapshots and bundles into an isolated project, matches dependency aliases to stable Package IDs, and invokes the **actual released** CLI: `version`, `check`, `inspect`, then optionally `build`.

It contains no second YAML semantic parser, inferred Owner generator or diagnostic suppression.

Expected private/published input layout (not checked into this repository):

~~~text
trusted-mas-project/
  trusted.json
  snapshots/
    ca-context/...
    ca-session-context/...
    mas/...
  capability/...
  evidence/...    # only when configured in trusted.json
~~~

Commands:

~~~bash
# Source check and dependency inspection, with JSON diagnostics
python scripts/compile_mas_v1alpha5.py --compiler skillc \
  --trusted-root ./trusted-mas-project --mode release

# Full deterministic artifact build, destination absent or empty
python scripts/compile_mas_v1alpha5.py --compiler skillc \
  --trusted-root ./trusted-mas-project --mode release \
  --out ./out/mas-v1alpha5
~~~

The adapter exits nonzero on any input or Compiler failure; stdout reports actual per-stage exit codes and diagnostics. Compiler must identify itself as `skillc v2.0.0`, target `connectionagent.io/v1alpha5`. There is no v1alpha4 fallback.

For strictly local synthetic compilation tests, select `--mode fixture`. The adapter then allows test-only `urn:example:` identities but reports `NOT_QUALIFIED` regardless of whether a static Build succeeds. Fixture artifacts are never eligible for live deployment. Default `--mode release` rejects `urn:example:` in Skill YAML and trusted.json.

Adapter input tests (not real Compiler conformance):

~~~bash
python -m unittest discover -s tests -p test_compile_mas_v1alpha5.py
~~~

## Exact current blockers

| Group | Required trusted export | Current status |
| --- | --- | --- |
| D1 | `ca-context`: Context Schema package, stable ID and snapshot digest | alias only, no resolved snapshot in official example |
| D2 | `ca-session-context`: SMF Observation ToolCatalog, result Schema and evidence/source authority | alias only |
| D3 | `mas`: 13 MAS Operation ToolCatalog entries, Owner identity, per-Operation Schemas, Effect/Outcome/Mutation contracts | `urn:example:connectionagent:openamsm-mas-tool-contracts` |
| C1 | Deployment CapabilityContracts for SMF read + 13 MAS Operations | 14 `urn:example:connectionagent:capability:*` candidates |
| S1 | MAS Predicate result Schema exports | 12 `urn:example:openamsm:mas:*` candidates |
| E1 | Source-authoritative Evidence Guarantees, scope/freshness, EvidenceTrustBindings | not published |
| T1 | Complete immutable Snapshot, trusted Owner bindings and deployment authorization | not provided here |

The Compiler recomputes snapshot digests, checks Schema/Owner/Capability closure, and verifies a successful artifact. **A source file that parses is not a compilable, authorized Skill.** A failure on untrusted or unpublished references is correct Compiler behavior, not a Compiler regression.

## Two acceptance gates

**A. Fixture static compilation.** For explicitly synthetic internally consistent trusted snapshots, real Compiler v2.0.0 Check, InspectDependencies and Build succeed, emitted manifest verifies, and negative tampering/Owner-mismatch tests fail closed. Only claim `FIXTURE_STATIC_BUILD_PASS`.

**B. Official MAS Skill.** Owner/Host/Deployment release actual ToolCatalog, Schemas, CapabilityContracts, Evidence and authorization; replace every placeholder with exact published identity; build against these immutable snapshots. Compiler success still does not imply Host/Runtime authorization or real 5GC E2E. Before this gate passes: `NOT_LINKABLE / NOT_QUALIFIED`.

## Adjacent issue not to hide

The current first MAS Node runs `SC.VALIDATE_SUBSCRIPTION` before observing that no SM Context exists. OpenAMSM's /invoke resolver may create an SMF session shell as a side effect, so the subsequent ABSENT test may reject a new UE/PSI. Correct that business admission ordering separately in [ca-skills #71](https://github.com/odango-chan/ca-skills/issues/71). Never suppress Compiler diagnostics to work around that mismatch.

## Ownership

- [ca-skills #71](https://github.com/odango-chan/ca-skills/issues/71): canonical source and trusted dependency closure.
- [ca-client-tools #10](https://github.com/odango-chan/ca-client-tools/issues/10): type-safe MAS Provider (private operation IDs are not public ToolCatalog identities).
- [ca-agent-demo #215](https://github.com/odango-chan/ca-agent-demo/issues/215): Compiler Artifact admission and actual execution on the existing graph engine.
- [Compiler v2.0.0](https://github.com/odango-chan/ca-skill-compiler/releases/tag/v2.0.0): already released, do not reopen its rewrite.
