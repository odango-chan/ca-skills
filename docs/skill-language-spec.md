# ConnectionAgent Skill Language Specification

**Version:** v0.1  
**Status:** Draft — source-derived language contract; not yet a compiler-conformance claim  
**Owner:** `ca-skills`  
**Consumers:** `ca-skill-compiler`, `ca-skill-studio-demo`, and the future LSP

This document extends the existing **One CA Authoring Language Core** in the authoring guide. It makes the current source vocabulary, artifact boundaries, reference roles and semantic-token taxonomy explicit. It does not introduce a second DSL.

## 1. Authority and scope

`ca-skills` owns the authoring semantics and the public source-language contract. This document is the canonical source for:

- the meaning and role of constructs used by official Skill source;
- the distinction between language keywords, user-defined identifiers and references;
- stable semantic-token IDs that editors and future language services consume;
- the boundary between current source syntax, documented-but-unverified syntax and future design.

The target Compiler implements this contract and supplies machine validation. Skill Studio consumes the token taxonomy for highlighting. A future LSP may use the same symbol and reference categories for diagnostics, completion, definition navigation and references.

The legacy `ca-skill-toolchain` schemas validate only the subset they model. They do not redefine or silently narrow the current source contract. In particular, the conventional PDU Session Skill contains node-level `preconditions` and `postconditions` that the legacy Procedure schema does not support. The target stateless Compiler must implement the documented source semantics or report an explicit unsupported-construct diagnostic; it must never silently drop them.

This v0 is derived from the two current 5GC packages and their imported Library snapshot. It is not a claim that the new Compiler, Linker or Runtime has accepted or executed every construct.

## 2. Language layers

The Skill authoring language is a composition of existing formats with ConnectionAgent-specific structure:

| Layer | Source | Language responsibility |
| --- | --- | --- |
| Model guidance | `SKILL.md` | Markdown plus standard Skill frontmatter; business meaning, applicability and safe-use guidance |
| Skill contract | `assurance/contract.yaml` | Skill identity, goal, entry Procedure, resource boundary and final conditions |
| Procedure | `assurance/procedure.yaml` | Deterministic graph, node intent, bindings, conditions and outcome routing |
| Predicate set | `assurance/predicates.yaml` | Required observations and deterministic evaluation over materialized evidence |
| Qualification case | `cases/<case>/case.yaml` | Scenario, fixture and expected semantic obligation |
| Governed script | `scripts/*.py` | Deterministic local computation with declared metadata and schemas |
| Skill schema | `schemas/*` | Skill-owned payload/schema definitions; JSON Schema keywords remain JSON Schema, not CA keywords |
| Supplemental knowledge | `references/*.md` | Optional Markdown knowledge; not executable syntax or evidence |
| Imported Library | `lib/**/*.yaml` | Read-only external contracts/catalogs referenced by Skill source |
| Generated output | `output/**` | Compiler-owned output; never authoring input |

Do not treat every YAML key as a reserved word. YAML is the serialization format; only keys and values in a defined ConnectionAgent position receive a CA semantic classification.

## 3. Current artifact forms

The lists below describe fields and forms present in the current source baseline or explicitly retained in the authoring reference. They do not imply that every legacy schema or compiler version accepts every form. Exact requiredness and constraints belong to the target machine schema.

### 3.1 `SKILL.md`

The frontmatter uses the standard Skill metadata fields `name` and `description`. The Markdown body is model-facing prose. Headings and ordinary domain words are not reserved CA keywords.

### 3.2 `SkillContract`

Current document identity:

```yaml
apiVersion: connectionagent.io/v1alpha1
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
    requiredFacts: []
  allowedResources:
    capabilities: []
    localTools: []
  postconditions: []
```

Recognized structural fields in the current authoring model include:

- `skillType`, `goal`, `entryProcedure`;
- `inputs.requestSchema`;
- `context.requiredFacts`;
- `allowedResources.capabilities` and `allowedResources.localTools`;
- contract-level `preconditions`, `requirements` and `postconditions`;
- `planning.maxActions` and `planning.allowDynamicProcedure`;
- `failureSemantics.outcomeUnknown.requireReconcile`.

Contract-level preconditions/postconditions are Skill-wide conditions. They are not the same construct as node-level Procedure preconditions/postconditions.

### 3.3 `Procedure`

The current source uses an object-form graph:

```yaml
procedures:
  <procedure-id>:
    inputs: {}
    start: <node-id>
    nodes:
      <node-id>:
        call: capability.operation
        with: {}
        'on': {}
```

The current 5GC source uses these node intents:

| Intent key | Meaning |
| --- | --- |
| `call` | Invoke a referenced governed Capability/Operation |
| `verify` | Evaluate a referenced Predicate |
| `script` | Run a governed local-computation Script |
| `reconcile` | Reconcile the exact original mutation node |
| `terminal` | End with a declared Procedure terminal result |

The authoring reference also documents `tool`, `procedure` and `for` forms. They are **documented but not demonstrated by the two current 5GC packages**; their target-Compiler support must be confirmed before they are treated as generally available syntax. Iteration must remain explicitly bounded and artifact-specific.

A Procedure may declare:

- `inputs.<name>.type` and `inputs.<name>.from`;
- `start` and `nodes`;
- `with.<argument>.from` or `with.<argument>.value`;
- an `'on'` outcome-to-node mapping;
- `applicability`, where the current conventional PDU Session source uses a `predicates` mapping;
- node-level `preconditions` and `postconditions`.

Do not infer that a node ID, input name, argument name or output field name is a reserved keyword. Those are author-defined identifiers.

### 3.4 Node-level preconditions and postconditions

The conventional PDU Session source uses ordered phases with `steps` and an `'on'` result map:

```yaml
preconditions:
  steps:
    - name: prepare-input
      script: scripts/prepare_input.py
  'on':
    PASS: continue
    FAIL: failed
    UNKNOWN: unresolved

postconditions:
  steps:
    - verify: example.operation_effective
  'on':
    PASS: next-business-node
    FAIL: failed
    UNKNOWN: unresolved
```

Preconditions are side-effect-free preparation immediately before the main operation. Postconditions establish the operation's business result before the Procedure advances. Their detailed ordering and failure semantics are defined in [Authoring Model](authoring-model.md).

These node-level fields are present in current source but are unsupported by the legacy `ca-skill-toolchain` Procedure schema. They are part of the target source contract, not permission to invent additional node fields.

### 3.5 Bindings and paths

A `with` argument has one explicit source:

- `from` — a path/reference into Procedure input, admitted context, a prior node result or a preparation result;
- `value` — a literal value.

Current path namespaces include `input.*`, `context.subject.*`, `context.request.*`, `context.facts.*`, `context.constraints.*`, `loop.*` where iteration is supported, and explicit producer paths such as `<node>.output.*` or `<node>.preconditions.<step>.output`.

A path is not an arbitrary string expression. Do not invent implicit previous-node binding, hidden interpolation, `fromContext`, or `fromOutput`.

### 3.6 Predicate set

Current document identity:

```yaml
apiVersion: connectionagent.io/v1alpha1
kind: PredicateSet
metadata:
  skill: establish-pdu-session
predicates:
  example.goal_satisfied:
    observations:
      state:
        ref: example.state.snapshot
        scope: '{}'
        freshness: 5s
    evaluator:
      type: cel
      expression: observations.state.status == "READY"
```

The source vocabulary includes:

- `predicates.<predicate-id>` definitions;
- `observations.<alias>.ref`, `scope` and `freshness`;
- `evaluator.type` with current source forms `cel` and `script`;
- `evaluator.expression` for CEL, or `evaluator.ref` for a governed Predicate Script.

The expression value is a CEL sub-language, not YAML or a CA keyword list. Predicate evaluation consumes already-materialized evidence; it does not acquire evidence or invoke Providers.

### 3.7 Qualification Case

Each Case is one `cases/<case-name>/case.yaml` file with document identity `kind: SkillTestCase`. Current source fields include `metadata.skill`, `metadata.name`, `spec.classes`, `spec.purpose`, `spec.context`, `spec.expect` and `spec.fixtures`.

A Case is a source-level semantic obligation. Its presence does not prove that it was executed, that a Runtime passed it, or that the Skill is qualified.

### 3.8 Governed Python Script

Skill-local Python Scripts are deterministic local computation. The documented metadata block is delimited by `# /// connectionagent-tool` and carries fields such as `name`, `inputSchema`, `outputSchema`, `effect`, `sandbox.network` and `timeout`.

Script metadata is not ordinary Python syntax. Script bodies remain Python and must use Python language tooling; the CA token taxonomy applies only to the metadata block and CA references to the script.

### 3.9 Imported ToolCatalog and Capability references

The current imported snapshot is `lib/tools/createdsession.tool.yaml`, a `ToolCatalog` document. Its operation definitions are under `spec.contracts[].operation`, with the associated adapter, effect, input schema and output schema declarations.

Keep three identities distinct:

- A **Capability ID** names an authorized resource group. The deployment-owned `CapabilityContracts` registry may map that ID to one or more exact Operation identities.
- An **Operation ID** names one exact callable operation. A Procedure node's `call` always references an Operation ID, never a Capability group.
- `contract.spec.allowedResources.capabilities[]` is the Skill's authorization upper bound. Its entries may be either a Capability ID or a direct Operation ID. The Host resolves a Capability ID through the deployment Capability registry, or accepts an exact Operation ID as a direct grant.

The ToolCatalog defines Operations; it is not itself the deployment Capability registry. A project may optionally import a read-only `CapabilityContracts` snapshot under `lib/capabilities/` when it needs source navigation for Capability IDs. This project does not currently import that deployment-owned registry. Without it, a named Capability ID cannot be linked to its definition file. An `allowedResources.capabilities[]` value that exactly matches an imported Operation may still link directly to that Operation.

For this project baseline:

- The conventional Skill's 12 `allowedResources.capabilities[]` entries are direct Operation grants, not the six grouped Capability IDs in the separate deployment registry. All 12 resolve by exact Operation identity in the imported ToolCatalog; the Procedure calls use those same Operation identities.
- The MAS Skill declares 16 `ca.pdu_session.*` Operation identities in both its resource allowlist and Procedure calls: 14 MAS business operations plus two Host-side resource-finalization/cleanup operations. None is present in the approved imported ToolCatalog. Its `design/tool-contract.yaml` is explicitly a design draft, not an approved ToolCatalog, so these references remain unresolved. Do not invent definitions or import the draft as an approved dependency.

A resolved import is a source/link fact only. It does not prove that an implementation is registered, deployed, READY, authorized or successfully executed.
## 4. Symbol and reference model

The following definition/reference pairs are the v0 navigation contract. Their machine-readable token IDs and source selectors are listed in [the semantic token catalog](../spec/skill-language-tokens.yaml):

| Definition | Definition location | Reference locations |
| --- | --- | --- |
| Skill | Skill package frontmatter `name` | Case `metadata.skill`; package-level references where explicitly defined |
| Procedure | `procedure.yaml: procedures.<id>` map key | Contract `entryProcedure`; child Procedure reference where supported |
| Procedure node | `procedure.yaml: procedures.*.nodes.<id>` map key | `start`, main-node `'on'` targets, `reconcile` target |
| Predicate | `predicates.yaml: predicates.<id>` map key | Procedure `verify`; Contract `predicate` fields; `applicability.predicates` |
| Capability | Imported `CapabilityContracts` `spec.capabilities[*].capability` (optional deployment-owned import) | Contract `allowedResources.capabilities[]` when the value is a Capability ID |
| Operation | Imported ToolCatalog `spec.contracts[].operation` | Procedure `call`; Contract `allowedResources.capabilities[]` when it directly grants an Operation |
| Case | `case.yaml: metadata.name` | Case `metadata.skill` identifies its owning Skill |
| Local Tool | Script metadata identity (mapping to the `skill.*` local-tool ID is not yet frozen) | Contract `allowedResources.localTools[]`; Procedure `tool` where supported; Predicate evaluator `ref` when it denotes a local Tool |
| Script | File under `scripts/` | Procedure `script` path |
| Schema | File under `schemas/` | Contract `requestSchema`; other schema refs where path-based |

Resolution rules:

1. Resolve exact identifiers and package-relative paths only. No fuzzy name matching.
2. Resolve Procedure `call` values to exact Operation definitions in the project's imported ToolCatalog.
3. Resolve `allowedResources.capabilities[]` values against an imported CapabilityContracts registry first; if no exact Capability ID is found, allow an exact ToolCatalog Operation match as a direct Operation grant. If neither target exists, keep the reference unresolved.
4. Resolve `reconcile` to the exact original mutation node in the same Procedure; it is not a Capability or Operation reference.
5. Keep unresolved references visible as unresolved. Syntax highlighting must not imply successful linking.
6. A name that appears in prose, a comment, a user-defined map key or an unrelated YAML field is not automatically a symbol reference.

These pairs define future Go-to-Definition and Find References behavior. Phase-one highlighting may classify a reference by its syntactic position without resolving its target.

## 5. Semantic-token taxonomy

The following token IDs are stable language-level categories. They are independent of editor theme colors and independent of LSP's eventual token-type encoding.

| Token ID | Apply to | Examples |
| --- | --- | --- |
| `ca.document.kind` | Values of document `kind` | `SkillContract`, `PredicateSet`, `SkillTestCase`, `ToolCatalog`, `CapabilityContracts` |
| `ca.document.version` | Values of `apiVersion` | `connectionagent.io/v1alpha1`, `ca-agent-host.capability-contracts/v1` |
| `ca.keyword.structure` | Known CA structural keys in their defined positions | `spec`, `metadata`, `procedures`, `nodes`, `predicates`, `observations` |
| `ca.keyword.control` | Node-intent keys | `call`, `verify`, `script`, `reconcile`, `terminal` |
| `ca.keyword.condition` | Condition/phase keys | `applicability`, `preconditions`, `postconditions`, `steps`, `'on'` |
| `ca.keyword.binding` | Binding keys | `with`, `from`, `value` |
| `ca.reference.capability` | Resource-grant values in `allowedResources.capabilities[]` (Capability ID or direct Operation grant) | `capability-id` |
| `ca.symbol.skill-definition` | Skill frontmatter name | `name: establish-pdu-session` |
| `ca.symbol.capability-definition` | Capability IDs in an optionally imported `CapabilityContracts` registry | `spec.capabilities[*].capability` |
| `ca.symbol.procedure-definition` | Procedure definition map keys | `procedures.<id>` |
| `ca.symbol.node-definition` | Procedure node definition map keys | `nodes.<id>` |
| `ca.symbol.predicate-definition` | Predicate definition map keys | `predicates.<id>` |
| `ca.symbol.case-definition` | Case `metadata.name` | `01-complete-profile` |
| `ca.symbol.local-tool-definition` | Local Tool identity in Script metadata | `# name: select-establishment-configuration` |
| `ca.symbol.operation-definition` | Imported Operation definition values | `spec.contracts[].operation` |
| `ca.reference.operation` | Exact Operation IDs in Procedure `call` positions | `sbi.udm.sm_data.get` |
| `ca.reference.predicate` | Predicate IDs in reference positions | `createdsession.ingress.eligible` |
| `ca.reference.procedure` | Procedure IDs in reference positions | `entryProcedure`, child Procedure reference |
| `ca.reference.node` | Procedure node IDs in reference positions | `start`, main-node `'on'` target, `reconcile` target |
| `ca.reference.local-tool` | Skill-local Tool IDs in reference positions | `skill.select-establishment-configuration` |
| `ca.reference.script` | Package-relative Script paths | `scripts/select_establishment_configuration.py` |
| `ca.reference.schema` | Package-relative schema paths or schema registry refs | `schemas/establishment-request.schema.yaml` |
| `ca.reference.binding-path` | Values of `from` | `input.ue`, `context.request.dnn` |
| `ca.value.outcome` | Outcome keys/expectations in defined result positions | `PASS`, `UNKNOWN`, `COMMITTED`, `OUTCOME_UNKNOWN` |
| `ca.value.effect` | Effect values in a Tool/Case contract | `READ`, `MUTATION`, `local_compute` |
| `ca.value.type` | Primitive type values in type declarations | `string`, `integer`, `object` |
| `ca.expression.cel` | CEL expression values | `observations.state.status == "READY"` |
| `ca.identifier.user-defined` | User-defined IDs and map/property names | Node IDs, input names, observation aliases, Case names |

Ordinary YAML and Python comments remain the responsibility of their existing language grammars; they are not a CA-specific semantic token. Classification is position-sensitive, not spelling-only. For example, `call` is a control keyword only as a node-intent key; the same word in prose or a user-defined field is ordinary text. Values under `allowedResources.capabilities` are resource-grant references; Procedure `call` values are Operation references. An arbitrary property named `status` is not a reserved CA token. The current `createdsession.*` Predicate/Observation names are ordinary user-defined identifiers, not a reserved prefix or a language keyword.

Outcome values remain owned by their result domain:

- Predicate outcomes: `PASS`, `FAIL`, `UNKNOWN`;
- Procedure terminal results: `SUCCEEDED`, `FAILED`, `UNRESOLVED`, `SAFE_STOPPED`;
- operation outcomes: declared by the referenced Operation contract, not one global hard-coded enum.

Effect values also depend on the declaring contract. Do not collapse `READ`, `read_only`, `MUTATION` and `local_compute` into one invented universal enum.

The machine-readable token ID registry is `spec/skill-language-tokens.yaml`; it records token IDs, source positions and symbol/reference selectors without editor-specific colors. The token taxonomy defines **what** a token is, not **which color** it receives. Skill Studio owns the theme mapping. The same token IDs must be reused by future LSP Semantic Tokens; do not create a Studio-only parallel vocabulary.

## 6. Current, pending and excluded syntax

| Construct | Current source status | Compiler status / rule |
| --- | --- | --- |
| Skill frontmatter, Contract, Procedure graph, PredicateSet and Case envelope | Present in the current package baseline | Validate against the target source contract |
| Procedure `call`, `verify`, `script`, `reconcile`, `terminal` | Present in current 5GC source | Recognize and implement |
| Node `preconditions` / `postconditions` | Present in conventional source | Legacy Toolchain unsupported; target Compiler must support |
| `applicability.predicates` | Present in conventional source | Preserve this observed form |
| `applicability.when` | Appears in an older authoring example, not the current two-package baseline | Not frozen by this v0; do not treat as equivalent to `predicates` |
| Procedure `tool`, child `procedure`, and `for` | Documented in earlier syntax guidance; not demonstrated in the current two-package baseline | Confirm target-Compiler semantics before claiming support |
| Rule source such as `rules.yaml`, `SkillRuleSet`, `ruleRefs` | Design-only; not in current Skill packages | Excluded from v0 syntax and highlighting as reserved CA keywords |
| Rule primitives `path / op / value` | Candidate shared primitives in the long-term Language Core | Not current reserved syntax |
| MAS Capability references | Declared in MAS source but absent from the imported ToolCatalog | Highlight as references; report unresolved until an approved catalog is imported |

## 7. Editor and LSP consumption

### Phase one: Skill Studio highlighting

Skill Studio may use YAML/TextMate context patterns to assign these token IDs (through namespaced TextMate scopes) and map them to the existing Studio theme. It must:

- preserve ordinary YAML syntax highlighting;
- classify CA keywords only in their defined structural positions;
- classify Capability, Predicate, Procedure, Script and Schema references by their field context;
- keep user-defined identifiers visually distinct from reserved syntax;
- avoid claiming reference resolution, validation or readiness from color alone.

No LSP server, diagnostics, completion or navigation is required for phase one.

### Future: LSP and Compiler

The Compiler parses and validates the source contract and builds the symbol/reference index. LSP consumes that index and the same token taxonomy for Semantic Tokens, diagnostics, completion, Go-to-Definition and Find References. The Compiler must not depend on Skill Studio, TextMate or theme configuration.

## 8. Change control and open decisions

A new reserved word, artifact kind, node intent, binding form, expression language or reference rule requires:

1. an update to this specification with examples and explicit support status;
2. a positive and negative source fixture;
3. a target-Compiler implementation/validation update;
4. a Skill Studio grammar/token update;
5. synchronized English/Chinese authoring guidance.

The following are intentionally not frozen by v0: Rule machine syntax; the exact semantics of `applicability.when`; general child-Procedure and iteration support; the complete cross-project Capability/Operation registry and version-resolution contract. Do not fill these gaps with editor-only guesses.

Related documents:

- [Authoring guide](authoring.md)
- [Authoring Model](authoring-model.md)
- [Practical authoring syntax](../.agents/skills/create-connectionagent-skill/references/authoring-syntax.md)
- [Current 5GC source baseline](current-5gc-skill-baseline.md)
