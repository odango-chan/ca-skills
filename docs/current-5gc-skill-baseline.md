# Current 5GC Skill Source Baseline

**Version scope (2026-11-17): LEGACY 5GC SOURCE; NOT CA-SL v1alpha5-CONFORMING.** The two current Contracts still identify `connectionagent.io/v1alpha1`, while the imported `lib/tools/createdsession.tool.yaml` uses `ca-agent-demo.tool/v1`; neither meets the v1alpha5 inherited exact external profile. There is no verified trusted CapabilityContracts/Owner publication here. The [CA-SL v1alpha5 language](skill-language-spec.v1alpha5.zh-CN.md) is FROZEN / RELEASED; Compiler/Studio/Host/Owner/5GC remain `NOT_QUALIFIED` under §45.2 / §L.13.2. Do not turn a legacy snapshot into a purported v1alpha5 publication by changing its version string.

## Source authority and behavior reference

- **Only official Skill source authority:** this `ca-skills` repository.
- **Current business/implementation reference:** `odango-chan/ca-agent-demo@4395982fa6efb97714b97901603b2dfb7018c4d0` (main at the time of source refresh).
- The two official 5GC Skill packages were originally synchronized from that reference. This refresh intentionally migrates their Script interface to the new ca-skills Script Contract; business Procedure order and Operation identities remain unchanged.
- Current ca-agent-demo checkout is not a second Skill source of truth. Changes to official Skill language/source are made here first, then consumers are updated separately.

## Official current packages

| Package | Before Script migration | Current source | Notes |
| --- | ---: | ---: | --- |
| `establish-pdu-session` | 59 files | 50 files | Five Scripts migrated; nine duplicate Script input/output Schema files removed |
| `establish-pdu-session-mas` | 11 files | 11 files | No Python Script; Procedure/Predicate business source retained |

The two Skill business flows remain separate. The conventional PDU Skill retains its Procedure graph, node-level preconditions/postconditions, scalar Operation calls, Predicate IDs and 36 Case obligations. The MAS Skill retains its policy-first candidate flow; its source references remain but its Tool Operations are not approved/imported.

## Script migration

The five conventional PDU Scripts use [Script Contract v0](script-contract.md):

| Script | Output declaration |
| --- | --- |
| `scripts/select_establishment_configuration.py` | `EstablishmentSelectionOutput` |
| `scripts/build_pcf_policy_inputs.py` | `PcfPolicyInputsOutput` (functional TypedDict for `5qi`) |
| `scripts/build_n1n2_delivery.py` | `N1N2DeliveryOutput` |
| `scripts/evaluate_udm_read.py` and `scripts/evaluate_transfer_start.py` | `PredicateEvaluationResult` |

All five use `main(input: dict) -> OutputTypedDict`. Procedure inputs derive from `with:` Producer bindings; Predicate evaluator inputs derive from the Host Predicate Evaluation Context and declared observations. There is no Script metadata block, Script Input Schema, Script Output Schema source file or independent `localTools` identity. Script business calculations were retained.

The `PcfPolicyInputsOutput` uses functional `TypedDict` for wire key `5qi`, which is not a valid Python class attribute name. Compiler must support functional TypedDict declarations.

## Procedure and Operation identity

`call` remains the current scalar form:

~~~yaml
call: sbi.udm.sm_data.get
~~~

It always identifies an exact Tool Operation, never a Capability group or a `{dependency, operation}` object. Operation resolution is against ToolCatalog files supplied to Compiler. Dependency acquisition and source identity belong to Studio/caller, not Skill source or Compiler.

## Official imported ToolCatalog

`lib/tools/createdsession.tool.yaml` is an exact read-only snapshot of:

`odango-chan/ca-agent-demo/tools/contracts/createdsession.tool.yaml`

Source blob: `05a34f38b9974742c9e2d85e0d432cf616ce01e8`

It declares 12 Operations used by the conventional Skill. The conventional Contract lists those exact Operation IDs as direct resource grants; Procedure calls use the same identities.

The MAS Skill declares 16 `ca.pdu_session.*` Operation IDs. None is present in the approved ToolCatalog. The MAS design ToolCatalog remains a draft and is not imported as an approved contract. All 16 references remain unresolved until the real Tool owner supplies an approved catalog.

## Missing external Owner Schemas

- **Tool Output Schema gap:** the imported `sbi.udm.sm_data.get` Operation currently exposes `result` as a broad `{type: object}` without nested properties. The selection Script reads nested subscription and provenance fields. The Compiler cannot statically validate those fields until the Tool Owner supplies a complete Output Schema; the removed Skill-owned Script Input Schema must not be restored as a workaround.


The conventional and MAS Contracts explicitly identify required logical Owner paths under `lib/host/` and `lib/observations/`. The current repository does **not** bundle those files. `lib/` currently contains only the 12-Operation ToolCatalog snapshot.

- Host Subject / Facts / Evidence Schemas are missing.
- Observation payload Schema is missing.
- `context.requiredFacts` lists identifiers only; it is not a replacement Schema.
- The Root Routing Profile is deployment configuration and is not an acceptable substitute.

Until actual Owner files are supplied in the BuildRequest, strict compilation of references to those namespaces must report `EXTERNAL_SCHEMA_MISSING`. This is a known dependency, not permission to fabricate Schemas.

## Cases and acceptance

The conventional package contains 36 Cases. They remain source-level semantic obligations and are not executed by this repository's verifier or Compiler. This refresh does not implement Qualification, a Case runner, Runtime admission, Tool execution or live 5GC validation.

## Compiler transition status

- [ca-skill-compiler PR #3](https://github.com/odango-chan/ca-skill-compiler/pull/3): v0 closeout verified and ready for review; full v0 implementation remains PARTIAL.
- [ca-skill-compiler PR #4](https://github.com/odango-chan/ca-skill-compiler/pull/4): narrowed Compiler-only v0.1 design; design only, not implemented.

Compiler consumes source and imported contract bytes, links and validates them, generates Script Output Schemas and returns output files. It does not acquire dependencies, manage a project, run Python, execute Tools, perform Qualification or claim Runtime readiness.
