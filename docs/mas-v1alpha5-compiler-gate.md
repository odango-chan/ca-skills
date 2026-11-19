# MAS Skill v1alpha5 — Compiler v2.0.1 gate

**State (2026-11-19): INPUT_BLOCKED / NOT_LINKABLE.** This is a reproducible compilation entrypoint and dependency inventory, **not** a claim of a successful formal Build or a published MAS Owner. Compiler v2.0.1 has been released: https://github.com/odango-chan/ca-skill-compiler/releases/tag/v2.0.1.

## Source of truth

Only `examples/skills/establish-pdu-session-mas/` from this repository is submitted to the v1alpha5 Compiler. The `ca-agent-demo/skills/establish-pdu-session-mas/` historical source and old `ca-skill-compiler/examples/ca-agent-demo-project/` are not current compiler inputs.

The official MAS example still contains a candidate `mas` dependency, **14 grammar-valid but unpublished DottedId Capability IDs**, and 12 candidate Predicate result Schema IDs. These have no published trusted Owner export. Disabling validation, suppressing diagnostics or renaming placeholders cannot make a trustworthy Owner.

Compiler v2.0.1 consumes complete, immutable source plus resolved snapshots and trusted deployment bindings. It is not a package installer or Owner publisher.

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

The adapter exits nonzero on any input or Compiler failure; stdout reports actual per-stage exit codes and diagnostics. Compiler must identify itself as `skillc v2.0.1`, target `connectionagent.io/v1alpha5`. There is no v1alpha4 fallback.

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
| C1 | Deployment CapabilityContracts for SMF read + 13 MAS Operations | 14 syntactically valid but **unpublished** DottedId candidates (`smf.session.context.query` and 13 `mas.*` IDs) |
| S1 | MAS Predicate result Schema exports | 12 `urn:example:openamsm:mas:*` candidates |
| E1 | Source-authoritative Evidence Guarantees, scope/freshness, EvidenceTrustBindings | not published |
| T1 | Complete immutable Snapshot, trusted Owner bindings and deployment authorization | not provided here |

The Compiler recomputes snapshot digests, checks Schema/Owner/Capability closure, and verifies a successful artifact. **A source file that parses is not a compilable, authorized Skill.** A failure on untrusted or unpublished references is correct Compiler behavior, not a Compiler regression.

## Two acceptance gates

**A. Fixture static compilation.** For explicitly synthetic internally consistent trusted snapshots, real Compiler v2.0.1 Check, InspectDependencies and Build succeed, emitted manifest verifies, and negative tampering/Owner-mismatch tests fail closed. Only claim `FIXTURE_STATIC_BUILD_PASS`.

**B. Official MAS Skill.** Owner/Host/Deployment release actual ToolCatalog, Schemas, CapabilityContracts, Evidence and authorization; replace every placeholder with exact published identity; build against these immutable snapshots. Compiler success still does not imply Host/Runtime authorization or real 5GC E2E. Before this gate passes: `NOT_LINKABLE / NOT_QUALIFIED`.

## Adjacent issue not to hide

The current first MAS Node runs `SC.VALIDATE_SUBSCRIPTION` before observing that no SM Context exists. OpenAMSM's /invoke resolver may create an SMF session shell as a side effect, so the subsequent ABSENT test may reject a new UE/PSI. Correct that business admission ordering separately in [ca-skills #71](https://github.com/odango-chan/ca-skills/issues/71). Never suppress Compiler diagnostics to work around that mismatch.

## Ownership

- [ca-skills #71](https://github.com/odango-chan/ca-skills/issues/71): canonical source and trusted dependency closure.
- [ca-client-tools #10](https://github.com/odango-chan/ca-client-tools/issues/10): type-safe MAS Provider (private operation IDs are not public ToolCatalog identities).
- [ca-agent-demo #215](https://github.com/odango-chan/ca-agent-demo/issues/215): Compiler Artifact admission and actual execution on the existing graph engine.
- [Compiler v2.0.1](https://github.com/odango-chan/ca-skill-compiler/releases/tag/v2.0.1): published YAML sibling-depth hotfix; unchanged CA-SL v1alpha5 interfaces.

## Actual native Compiler acceptance (2026-11-19)

The real v2.0.0 release binary (SHA256 asset verification PASS) reported four error classes against the original MAS source:

- `IDENTIFIER_INVALID` for 14 Contract Capability IDs that had been formatted as URNs rather than DottedIds — **fixed in this PR** without asserting that the candidate DottedIds are published.
- `YAML_PARSE_ERROR` at Procedure line 260, “YAML indentation depth exceeds 64” despite shallow nodes — traced to a genuine Compiler tokenizer depth bug. [Compiler PR #44](https://github.com/odango-chan/ca-skill-compiler/pull/44) corrected this in `ca-skill-compiler/main`, preserving AST/alias depth limits. Full Go, vet, Native/WASM and real Chromium CI passed.
- `DEPENDENCY_SNAPSHOT_MISSING` and `EVIDENCE_GUARANTEE_LINK_INVALID` — correct fail-closed responses to unpublished Owner artifacts.

Earlier ca-skills Action [source validation run 44350887603](https://github.com/odango-chan/ca-skills/actions/runs/44350887603) invoked both the immutable official v2.0.0 release and the pinned patched Compiler. With the patched Compiler + corrected DottedIds, **no `YAML_PARSE_ERROR` or `IDENTIFIER_INVALID` remained**. Remaining static errors were `DEPENDENCY_SNAPSHOT_MISSING`, `EVIDENCE_GUARANTEE_LINK_INVALID` and `PREDICATE_EVIDENCE_UNSATISFIABLE`, all attributable to the unresolved trusted dependency/evidence closure.

Compiler **v2.0.1 is now officially published**, with all Native/WASM assets and independent SHA256 re-download verification passing in [release workflow 44352588675](https://github.com/odango-chan/ca-skill-compiler/actions/runs/44352588675). The v2.0.0 artifact remains immutable; use v2.0.1 for current MAS source. **This is source-grammar acceptance and fail-closed dependency validation, not a successful complete Build.**

## MAS source-contract mapping now available (not an Owner release)

[ca-client-tools PR #11](https://github.com/odango-chan/ca-client-tools/pull/11) has merged into the private Provider repository's main as a **non-deployable source-contract candidate**. It supplies a pinned OpenAMSM reference map for 13 MAS operations, 13 CA-facing input Schemas, 12 normalized result Schemas, and explicit CA-SL-to-OES argument mappings. The fixed policy-first Plan's 13 MAS/op/input/output records were independently compared to the candidate; 25/25 JSON Schema shapes were checked for their `$id`, required fields and closed-object declaration.

**This does not unblock a formal Build.** The candidate explicitly has no published Owner identity, no trusted ToolCatalog, no real Mutation Receipt/Commit Proof, no durable exact-occurrence Reconcile, no authorized CapabilityContracts, and no proven Evidence Guarantees. Its result Schema IDs remain `urn:example:`. Do not copy the candidate into a trusted DependencySnapshot or change `NOT_LINKABLE` to `QUALIFIED` merely because source-aligned Schema files exist.

The current OpenAMSM `MasInvokeResponse` contains an `OK` status plus business outputs, not an Owner-issued receipt binding `originalInvocationId` to `COMMITTED` / `NOT_COMMITTED`. The Provider's implemented runtime is currently read-only; MAS mutation handling must actually be implemented and verified before releasing such proof. The private Provider GitHub Actions run [44433042075](https://github.com/odango-chan/ca-client-tools/actions/runs/44433042075) reported failure with no executed job steps, so no Go or Python verifier CI pass is claimed for the candidate.

**Next qualification gate:** complete the actual 13-operation typed Provider, persisted/reconciled Owner evidence contract and authoritative deployment grants; produce an immutable authorized snapshot, then re-run released Compiler v2.0.1 `check`, `inspect`, `build` and artifact verification. The source package must still pass the separate first-node SMF session-absence business sequencing review.

