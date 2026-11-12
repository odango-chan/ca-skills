# Semantic Field Identity Contract vNext — proposal

Status: **DESIGN-REVIEW / NOT ADOPTED IN v0.2**  
Authority: `ca-skills` Skill Language; implementation experiments live in the isolated Compiler binding spike.

## 1. Problem

Input/output JSON Schemas constrain values, but ordinary field names and types do **not** uniquely identify business meaning. The same string `stateRef` may represent a subscription, policy, context, N4, or forwarding state. Conversely, MAS `input.ue` and an Operation `ueRef` refer to the same logical session-scoped subject.

The compiler must not auto-connect these values based only on same property name or type.

## 2. Proposed minimal contract

An optional **semantic field identity** is a stable identifier attached to an existing *owner-controlled field contract*. This is an annotation, not a new data value, default, permission or source binding.

Proposed key (subject to syntax freeze): `x-ca-semanticId`, usable on relevant JSON Schema property definitions. `x-` distinguishes an authoring extension from JSON Schema validation keywords and preserves compatibility with Draft 2020-12 readers. A future machine schema must explicitly admit and validate this annotation before implementation.

Illustrative Operation-owned Input Schema excerpt:

```yaml
inputSchema:
  type: object
  required: [ueRef, lifecycleRef]
  properties:
    ueRef:
      type: string
      x-ca-semanticId: session.subject.ue
    lifecycleRef:
      type: string
      x-ca-semanticId: invocation.lifecycle
```

Illustrative Host-owned Context Schema excerpt:

```yaml
properties:
  ueRef:
    type: string
    x-ca-semanticId: session.subject.ue
```

Each annotation owner **declares what the field means**, never a `from: subject.ueRef` path. Operation/Tool Owner does not know the Skill-specific Host context path. Context Schema Owner does not get to re-interpret the Operation's input type. Skill/Procedure controls the allowed context projection and explicit exceptions.

A unique semantic ID is a necessary **but not sufficient** condition for auto-binding. Type and constraint implication, nullability, scope/subject/lifecycle generation, producer identity, dominance, Effect and permission must also be checked where applicable.

## 3. Identity governance

- IDs are namespace-qualified (e.g. `session.subject.ue`, `invocation.lifecycle`, `invocation.ingress`, `session.pduSessionId`). Names are **proposed** and may be revised before freeze.
- An ID identifies **one precise business meaning**, not a common representation (`string`, `Ref`, `stateRef` are insufficient).
- Versioned contract authority assigns and reviews IDs. Host/Context authority owns context annotations; Operation Owner owns Operation inputs/outputs; `ca-skills` owns the shared authoring rules and cross-owner compatibility constraints.
- When two owners assert the same ID, the compiler must validate both schemas and trusted scope/authority constraints; duplicate IDs alone are not permission to bind.
- IDs are non-secret descriptive metadata. Their source contract digest/version must be part of the compiler's resolved build input.
- A contract must not assign the same ID to different generations of state merely to make binding automatic. Explicit producer lineage remains mandatory for handles whose meaning depends on operation instance or generation.
- Missing/unknown ID for a required automatic binding: **no auto-binding**; explicit `with/from` remains valid and required.
- Unsupported/malformed annotations fail closed; no string similarity fallback.

## 4. Illustrative 11 common MAS context semantics

These are candidate identities to validate against the actual owner contracts, not modifications to the existing ToolCatalog:

| MAS Procedure input | MAS Operation input | Candidate semantic ID |
|---|---|---|
| `ue` | `ueRef` | `session.subject.ue` |
| `ingress` | `ingressRef` | `invocation.ingress` |
| `lifecycle` | `lifecycleRef` | `invocation.lifecycle` |
| `pduSessionId` | `pduSessionId` | `session.pduSessionId` |
| `pti` | `pti` | `session.pti` |
| `requestType` | `requestType` | `session.requestType` |
| `dnn` | `dnn` | `session.dnn` |
| `sNssai` | `sNssai` | `session.sNssai` |
| `servingPlmn` | `servingPlmn` | `session.servingPlmn` |
| `requestedPduSessionType` | `requestedPduSessionType` | `session.requestedPduSessionType` |
| `requestedSscMode` | `requestedSscMode` | `session.requestedSscMode` |

Source: actual `establish-pdu-session-mas` Procedure and proposed MAS ToolCatalog. These are **test annotations**, not an assertion that the proposed MAS ToolCatalog is an approved owner contract.

The exact common field names are not an instruction to bind every field to matching context paths globally. The context projection is still scoped by the invoked Procedure.

## 5. Automatic and explicit bindings

- Contract-derived common context inputs may be auto-bound when unique and statically available.
- Resource handles and produced results such as `subscriptionStateRef`, `policyStateRef`, `n4Seid`, and `stateRef` remain explicit unless an output's semantic identity **plus exact producer instance and control-flow guarantees** prove the source unique.
- When an Operation requires a value that is only present in one branch, a global semantic match is not enough: fail closed or require a language-level guarded path.
- Preserve `with/from` for intentional override, selection, and exact lineage; do not introduce a new mandatory `bindings.yaml`.
- The compiler emits a complete Binding Plan with source path, semantic identity, owner contract, source producer identity, and proof/diagnostic of availability.

## 6. Scope and unresolved design

This document does not define a full semantic-type registry, new package manager, new Host data structure, or a new Operation identity. It does **not** modify v0.2 or authorize runtime inference.

Before final freeze: decide the exact extension-key spelling; validate the annotation against all current JSON Schema validation rules; confirm trusted context owner schemas; prove real Procedure CFG/dataflow; and compare compiled bindings with the existing explicit mappings and execution outcomes in both official Skills.

Related: [Capability & Authoring Model vNext](capability-authoring-model-vnext.md), [Binding Migration Rehearsal](binding-migration-rehearsal-vnext.md), [Observation Owner Inventory](observation-owner-inventory-vnext.md), and [Compiler PR #7](https://github.com/odango-chan/ca-skill-compiler/pull/7).


## 7. Compiler integration finding (2026-11-12)

The Compiler v0.1 source already provides schema implication and control-flow availability checks (`schemasCompatible`, `bindingSourceAvailable` / `nodeOutputDominates`, and `checkBindings`). The vNext Resolver must be a candidate generator only and submit its in-memory candidates to those existing checks. A second semantic type checker or a second CFG analysis would create inconsistent sources of truth.

See [Compiler Semantic Binding Integration Design](https://github.com/odango-chan/ca-skill-compiler/blob/spike/vnext-binding-resolver-20261112/docs/semantic-binding-integration-vnext.md).

The pinned Compiler demo project currently lacks the declared Context Owner Schemas for some `context.subject` / `context.facts` paths referenced by the two Procedures. This is a fixture completeness gap, not permission for Compiler to infer a Host schema. Migration tests must provide the actual owner-approved schemas and declare them in SkillContract before claiming whole-Procedure compilation.
