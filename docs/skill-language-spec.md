# ConnectionAgent Skill Language Specification

**Version:** vNext (breaking; demo-stage contract)
**API version:** `connectionagent.io/v1alpha2`
**Status:** Normative source-language contract for the vNext Compiler.
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
    ueRef:
      from: input.ueRef
    dnn:
      from: input.dnn
```

Bindings are explicit. A binding has exactly one of `from` or `value`. The source must resolve to an authoritative Producer Schema and be available on every path reaching the consumer.

Procedure inputs are named projections from the frozen invocation context:

```yaml
inputs:
  ueRef:
    from: context.subject.ueRef
  ingress:
    from: context.ingress
```

There is no implicit previous-node binding, dynamic selector, string interpolation, hidden context injection, automatic binding or semantic-ID resolver in this initial vNext implementation. The exact `with` mapping is the contract. Semantic-ID-assisted suggestions may be considered later as editor assistance, but they do not change source semantics or replace explicit bindings.

Node `preconditions` and `postconditions` remain ordered phases. They may contain only the supported phase actions and must declare their result routes. A Mutation result being committed does not by itself prove a business Predicate.

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
- implicit or automatic data binding.

There is no compatibility layer or parallel v0.2 execution path. Existing 5GC business behavior and its verified network contracts are migrated to the new source model; obsolete implementation structure may be replaced.
