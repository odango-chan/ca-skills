# ConnectionAgent Skill Language Specification

**Version:** vNext (breaking; demo-stage contract)
**API version:** `connectionagent.io/v1alpha2`
**Status:** Proposed source-language contract; binding syntax and semantics remain under DESIGN-REVIEW and are not frozen.
**Owner:** `ca-skills`
**Consumers:** `ca-skill-compiler`, Skill Studio, Runtime and future LSP.

This version replaces the v0.2 authoring model. It is not a compatibility extension: a vNext Compiler must reject v0.2 source forms rather than silently translating or preserving them.

## 1. Authority and boundaries

`ca-skills` is the only authority for Skill-authored language semantics and official Skill source. The current `ca-agent-demo` implementation is a source of verified business behavior and Owner implementation facts, not a second language source.

- This document defines source meaning, identities, binding positions and static validation.
- [Script Contract](script-contract.md) defines Skill-owned deterministic Python.
- [Schema Ownership](schema-ownership.md) defines the producer of each contract.
- [Authoring Model](authoring-model.md) defines Procedure semantics.
- The Compiler parses, links and validates caller-supplied bytes. It does not execute Tools or Scripts, acquire dependencies, manage a package library, or qualify a Skill.
- Runtime owns actual authorization, Effect enforcement, Provider dispatch, Evidence validation and execution outcomes.
- A successful build is not proof of Runtime readiness or live 5GC success.

## 2. Source package

A Skill package contains:

| Source | Responsibility |
|---|---|
| `SKILL.md` | Model-facing business guidance |
| `assurance/contract.yaml` | Skill identity, request/context contracts, Capability grants and final conditions |
| `assurance/procedure.yaml` | Deterministic Procedure graph, calls, Scripts, Predicate checks, bindings and routes |
| `assurance/predicates.yaml` | Pure Predicate definitions over explicitly supplied inputs |
| `cases/*/case.yaml` | Scenario and expected semantic obligation; not an execution engine |
| `scripts/*.py` | Skill-owned deterministic local computation |
| `schemas/**` | Skill-owned public Request and other genuinely Skill-owned schemas |
| `references/**/*.md` | Optional model knowledge, not executable syntax or Evidence |

There is no package-local `lib/` directory. Imported contracts are supplied by Skill Studio/caller as dependency snapshots in the Compiler BuildRequest. There is no physical `output/` input directory.

## 3. Dependency snapshots and identities

The caller supplies all source bytes required for one compilation:

- Skill source files under `skills/**`.
- Imported ToolCatalog and Owner Schema files grouped into dependency snapshots. Each snapshot has a caller-owned alias and a file set.
- One deployment-owned CapabilityContracts document, supplied separately from ordinary dependencies.
- Optional selected Skill targets.

Dependency aliases are used only to identify an imported contract unambiguously. They are not file paths and do not create a package-manager lifecycle.

References to imported contracts use `<dependency-alias>::<exported-id>`:

- Tool call: `fivegc-tools::sbi.udm.sm_data.get`
- Owner Schema: `host-context::urn:connectionagent:5gc:skill-context:ingress:v1`

The exported ID after `::` is the exact Operation ID or Schema `$id`. No Git URL, local `lib/` path, branch, registry address, digest, lockfile or source acquisition instruction appears in Skill source.

Operation IDs and Schema IDs remain Owner-defined. The alias selects the supplied snapshot; it does not rename or own the exported contract.

## 4. SkillContract

Canonical form:

```yaml
apiVersion: connectionagent.io/v1alpha2
kind: SkillContract
metadata:
  name: establish-pdu-session
spec:
  skillType: executable
  goal: pdu_session.initial_request_fulfilled
  entryProcedure: ue-requested-pdu-session-establishment
  inputs:
    requestSchema: schemas/establishment-request.schema.yaml
  context:
    projections:
      subject: host-context::urn:connectionagent:5gc:skill-context:subject:v1
      facts: host-context::urn:connectionagent:5gc:skill-context:facts:v1
      ingress: host-context::urn:connectionagent:5gc:skill-context:ingress:v1
    evidenceSchema: host-context::urn:connectionagent:host:predicate-evidence-refs:v1
  allowedResources:
    capabilities:
      - provider-5gc.createdsession.udm
      - env-fabric.createdsession.hold
      - ca-agent-host.createdsession.runtime
```

Rules:

- `inputs.requestSchema` is a Skill-owned public Request Schema path.
- `context.projections` declares the exact Host/Owner projections the Skill may consume. Each value is an alias-qualified exported Schema ID.
- `context.evidenceSchema` identifies the Host-owned bounded Evidence-reference projection. Evidence is separate from business data.
- `allowedResources.capabilities[]` contains Capability IDs only. Direct Operation IDs are forbidden here.
- The CapabilityContracts document maps each exact Operation ID to exactly one Capability and declares its Effect. The Compiler verifies that every called Operation is mapped, its Effect matches ToolCatalog, and its Capability is granted by this Skill.
- Runtime repeats authorization and Effect checks at execution. A static grant is not execution authority.
- There is no `allowedResources.localTools`, `requiredFacts` fallback, or physical `lib/` schema path.

## 5. Procedure and bindings

A Procedure is an explicit graph. Supported main-node actions are:

- `call`: one exact imported Operation.
- `script`: one Skill-owned Script.
- `procedure`: one local or explicitly identified cross-Skill Procedure.
- `verify`: one Predicate over already-materialized inputs.
- `reconcile`: reconciliation of the exact original mutation.
- `terminal`: a declared Procedure terminal result.

A Tool call names an Operation, not a Capability:

```yaml
read-subscription:
  call: fivegc-tools::sbi.udm.sm_data.get
  with:
    from: input
    sNssai:
      from: input.slice
```

### 5.1 Binding and minimal-input rules

A binding map is a projection into the callee's declared input contract, not a copy of the caller's context.

- The callee's declared input contract defines the only permitted target fields. Extra caller fields are never forwarded.
- `with.from: input` is an explicit opt-in same-name default source. It binds only same-named **required** callee inputs from the current caller's `input.<name>`.
- Optional callee inputs are omitted by default, even if the caller has same-named fields. To pass one, add an explicit target binding.
- Explicit target bindings override the default source for that target. They may rename the source or select an explicitly permitted Context/producer path.
- A required target not supplied by the default or an explicit binding is a compile error. The shorthand does not fall back to Context, prior nodes, parent state or other ambient sources.
- Without the shorthand, bindings remain explicit unless a separately specified contract-derived unique binding rule applies. No field-name guessing is permitted.
- `from: input` is valid only when the callee has a declared input contract: Operation Input Schema, Procedure input declaration or Predicate input declaration. It is not valid for Procedure Scripts, whose input projection is defined by their call-site bindings and has no independent declared input-name contract.
- All bindings, whether authored or generated by the shorthand, undergo identical Schema, type/nullability, producer-availability, scope, authorization and control-flow checks.

The shorthand is a compile-time projection rule. It does not forward all fields, create Runtime context inheritance, or add a new implicit parameter channel. Its final reserved-key syntax remains under review; the grammar must support arbitrary Owner-defined input property names without collision with shorthand metadata.

### 5.2 Required, optional and absent values

- Requiredness belongs to the callee's owning input contract. Do not repeat `required` in every call-site binding.
- A required Operation parameter must be bound. If the Operation contract requires a value the business operation does not actually need, fix the Owner contract; do not invent a placeholder or bypass validation.
- Optional Operation parameters are absent unless deliberately bound. Omission is not the same as `null`; explicit `null` is allowed only when the input Schema permits it.
- JSON Schema `default` is an annotation and does not authorize Compiler/Runtime value synthesis. Operational defaults must be defined by the contract owner.
- A caller may expose more fields than a callee consumes. Unused fields remain outside the callee's input projection.

### 5.2.1 Conditional availability and semantic identity

- A same-name default is an author-selected projection, not a heuristic search. Where source and target contracts publish semantic-field identities, they must agree; a conflict is a compile error.
- If semantic-field identities are absent, `with.from: input` records the author's explicit same-name intent for that one call site. This does not authorize name-based matching across Context, prior nodes or unrelated consumers.
- A source produced only on one control-flow branch may satisfy a consumer only when it is available on every path reaching that consumer. Prefer placing the consumer inside the branch that establishes the value.
- Do not replace an unavailable value with `null`. Optional absence is valid only when the consumer contract explicitly permits omission.
- Same-name binding does not flatten nested objects, extract nested properties, coerce types or normalize values. Such changes require explicit paths and declared deterministic transforms.


### 5.3 Procedure inputs and Context projections

- `context.projections` declares which approved Context projections a Skill may access; it does not inject them into Procedure or Operation inputs.
- `Procedure.inputs` declares only the Procedure's actual input interface. Do not mirror every Request or Context field.
- A Procedure may expose a value when it is consumed by that Procedure or intentionally shared with descendants. Otherwise bind directly from an explicitly permitted source at the consuming boundary.
- A child Procedure receives only its declared inputs. Parent Context is never implicitly inherited.

### 5.4 Predicate and Script input boundaries

- Predicate `inputs` declares only the business values used by its evaluator. Procedure `verify.with` supplies those values; Host/Runtime attaches Evidence separately.
- Procedure Script inputs are the exact keys in that Script call site's `with`. Do not pass unused Producer outputs.
- Script has no separate authored Input Schema in vNext. Therefore `with.from: input` is not supported for Script calls until a separately reviewed, statically checkable Script input declaration exists.
- No hidden `subject`, `request`, `facts` or `observations` globals are injected into Predicate or Script business input.

A binding has exactly one of `from` or `value`. A `from` source must resolve to an authoritative Producer Schema and be available on every path reaching the consumer. Literals are checked against the declared consumer type. No implicit previous-node binding, dynamic selector, string interpolation or Runtime parameter guessing exists.
 
## 6. Pure PredicateSet

Predicates no longer declare Observation references, scopes or freshness. They do not acquire data.

A Predicate declares the names it consumes. Procedure `verify.with` supplies those inputs:

```yaml
predicates:
  createdsession.ingress.eligible:
    inputs:
      ingress: {}
      request: {}
    evaluator:
      type: cel
      expression: input.ingress.requestType == input.request.requestType &&
        input.ingress.pti == input.request.pti &&
        input.ingress.messageType == 193 &&
        input.ingress.bindingStatus == "CURRENT" &&
        input.ingress.actionAuthorized == true
```

The matching Procedure node supplies both values explicitly:

```yaml
verify: createdsession.ingress.eligible
with:
  ingress:
    from: context.ingress
  request:
    from: input.request
```

Rules:

- Predicate input names are the only business-data names visible to its evaluator.
- CEL reads `input.<name>`; it does not read hidden `subject`, `request`, `facts` or `observations` globals.
- Script evaluators receive the same `input` object.
- The Host may attach a reserved `input.evidence` projection. It is not business data and cannot be authored or overwritten by Skill `with` bindings.
- Host validates the provenance, correlation, freshness and exact producer Evidence before a definite Predicate verdict is allowed.
- Predicate Scripts may cite only Evidence references attached to their own inputs. Their `evidenceUsed` output is a subset declaration, not an authority grant.
- Missing, ambiguous, stale or mismatched input/Evidence produces UNKNOWN. The evaluator must not reacquire data or perform network I/O.

## 7. READ Operations, Evidence and waiting

Data acquisition is explicit in Procedure as a READ Operation. Its output contains the normalized typed value; the same invocation returns the Evidence for that value. A Predicate consumes that exact output through `verify.with`.

Do not create a second read merely to reconstruct Evidence for a prior Tool result. Do not treat a local handle, Mutation success or a stale per-UE lookup as current network truth.

Bounded waiting remains a Host Runtime Operation (`ca-agent-host::ca.session.evidence.await`), not a Predicate feature and not a domain Observation identity. It receives:

- the exact READ Operation ID to poll;
- the exact scope/bindings for that Operation;
- a bounded freshness and wait budget;
- an explicit absence policy.

The wait returns only a wait/evidence summary. After the wait, Procedure performs the final READ Operation separately and passes that final output to the Predicate. The wait and final read must use the same exact attempt selector. The polled READ Operation must also be included in the Skill's Capability grants.

## 8. Script Contract

The only entry point is:

```python
def main(input: dict) -> OutputType:
    ...
```

- The parameter is named `input` and annotated exactly `dict`.
- Procedure Script input is derived from that call site's `with` bindings.
- Predicate Script input is the declared Predicate input projection plus Host-attached Evidence refs.
- The return annotation names a non-empty `TypedDict` declared in the same file.
- Compiler statically derives a closed Draft 2020-12 Output Schema from supported type declarations. It does not execute Python.
- `Any`, `object`, open `dict` outputs, empty output types, unsupported unions and inferred function-body schemas are forbidden.
- Scripts are deterministic local computation only. They do not call Tools, HTTP, MCP, Providers, shells or other external systems.

The old `connectionagent-tool` metadata, local Tool IDs and separately authored Script Input Schemas are not part of vNext.

## 9. Cases and References

Cases remain source-level semantic obligations. The 36 established 5GC Cases and three References are business-behavior reference material for the migration. They are not a Compiler execution engine and do not require a separate migration rehearsal.

The 5GC Skill is the executable migration baseline. MAS remains a design/example package until its own Operations and Owner contracts are actually available; it is not a prerequisite for 5GC acceptance.

## 10. Compiler boundary and acceptance

Compiler:

- accepts Skill files, dependency snapshots, one CapabilityContracts document and optional targets;
- parses only vNext source;
- links exact Operation, Capability and Schema identities;
- validates Producer/Consumer bindings and control-flow availability;
- derives Script Output Schemas;
- returns deterministic diagnostics and build output files.

Compiler does not:

- acquire or refresh dependencies;
- manage packages, manifests, lockfiles, registries or caches;
- compute or export dependency digests;
- execute Scripts or Tools;
- bind Runtime Providers or credentials;
- qualify or execute Cases;
- claim Runtime READY or live network success.

A vNext build fails closed on missing or ambiguous Owner Schemas, duplicate exported IDs, missing Capability mappings, ungranted Capabilities, Effect mismatch, unsupported v0.2 constructs, invalid bindings or missing Script contracts.

## 11. Breaking change

The following v0.2 forms are rejected, not translated:

- `apiVersion: connectionagent.io/v1alpha1` for SkillContract/PredicateSet;
- Predicate `observations`, `scope`, `freshness` and evaluator access to implicit context globals;
- physical `lib/**` references in Skill source;
- direct Operation IDs in `allowedResources.capabilities`;
- local Tools and `connectionagent-tool` Script metadata;
- v0.2 implicit context/previous-node forwarding or runtime parameter guessing. vNext's opt-in `with.from: input` projection is defined in §5 and is not blanket or ambient binding.

There is no compatibility layer or parallel v0.2 execution path. Existing 5GC business behavior and its verified network contracts are migrated to the new source model; obsolete implementation structure may be replaced.
