---
name: create-connectionagent-skill
description: Use when authoring, reviewing or refreshing ConnectionAgent Skill source in ca-skills. Apply the current CA-SL v1alpha5 specification and keep historical 5GC packages on their documented source baseline.
---

# Author ConnectionAgent Skill source

## Choose the source baseline

- Read the [current CA-SL specification](../../../docs/skill-language-spec.md) and [authoring guide](../../../docs/authoring.md). Use the [v1alpha5 examples](../../../examples/README.md) for new source.
- Read the [legacy 5GC baseline](../../../docs/current-5gc-skill-baseline.md) before editing packages under `skills/`. Preserve business ordering and callable identities unless the requested migration changes them.
- Read [Skill granularity](references/skill-granularity.md) when deciding whether a behavior belongs in a Skill, Tool or routing policy.

## Author and review

1. Keep `SKILL.md` focused on goal, applicability, supported profile, business inputs, completion and uncertainty. Put protocol and source traceability in `references/`.
2. For deterministic Skills, maintain `assurance/contract.yaml`, `procedure.yaml` and `predicates.yaml`. Use explicit arguments, exact callable exports and a final Postcondition that proves the Goal. Read the [syntax references](references/authoring-syntax.md) for the authoritative sections.
3. Put Skill-owned Schemas in `schemas/`. Link caller-supplied Owner contracts for Tool, Host and Observation types. Keep local computation in pure Scripts and derive Script inputs from the declared source bindings or Predicate signature.
4. Record semantic cases under `cases/<case>/case.yaml` and optional model knowledge under `references/`. Keep verification results tied to the gate that actually ran.

Run `make verify` for repository checks. Report Compiler, linking, Runtime and live acceptance separately when their respective implementations have been exercised.
