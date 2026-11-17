# IngressCatalog Diagnostic Registry v1alpha1

**Registry ID:** `connectionagent.io/ingress-diagnostics/v1alpha1`  
**Applies to:** `connectionagent.io/ingresscatalog/v1alpha1` / `IngressCatalog`  
**Status:** NORMATIVE DRAFT — NOT FROZEN  
**Normative machine-readable source:** [ingress-diagnostic-registry-v1alpha1.json](ingress-diagnostic-registry-v1alpha1.json)

## 1. Ownership and versioning

This registry owns only static diagnostics for declarations owned by the IngressCatalog contract. Its version is independent of CA-SL and Compiler releases. For `connectionagent.io/ingresscatalog/v1alpha1`, the registry is exactly `connectionagent.io/ingress-diagnostics/v1alpha1`; consumers MUST NOT infer another registry from a similar version string.

The registry does not redefine or shadow CA-SL diagnostics for YAML parsing, dependency trust, Owner identity, ToolCatalog export linking, Schema resolution, SourcePath, type assignment or Skill-specific Wait semantics. The Code strings in this registry are globally unique. Diagnostic identity remains the CA-SL composite `(Code, Phase)`; `registryId` is provenance and does not create a second identity namespace.

## 2. Common diagnostic contract

Every entry in this registry has:

- `Phase = C_STATIC`;
- `Severity = ERROR`;
- build-blocking disposition;
- one stable `messageKey` and canonical message template;
- one primary source location in the exact IngressCatalog dependency snapshot.

The logical Compiler `Diagnostic[]` record for an Ingress-owned diagnostic MUST preserve these attributes:

| Attribute | Required meaning |
|---|---|
| `code` | Exact Code from this registry |
| `phase` | `C_STATIC` |
| `severity` | `ERROR` |
| `registryId` | `connectionagent.io/ingress-diagnostics/v1alpha1` |
| `messageKey` | Exact stable key from the registry |
| `sourceLocation` | `dependencyAlias`, `snapshotPath`, and RFC 6901 `jsonPointer` |
| `relatedLocations` | Optional locations needed to explain a duplicate or cross-artifact mismatch |

The physical serialization of the Compiler Diagnostic envelope remains owned by the Compiler Artifact/Diagnostic protocol. That protocol MUST preserve the logical attributes above without renaming, dropping or conflating `code`, `phase`, `registryId` or source location. Build blocking is derived from `C_STATIC + ERROR`; it is not a new Skill Outcome.

A source location MUST point into the exact immutable Catalog snapshot that was admitted for this Build. `jsonPointer` is an RFC 6901 pointer prefixed by `#`. If a required field is absent, point to the nearest existing containing object. For a duplicate, the primary location is the later occurrence and `relatedLocations` contains the first occurrence. Optional line/column coordinates are display hints derived from that exact snapshot; they are not identity or ordering inputs.

## 3. Diagnostic ownership boundary

| Condition | Required diagnostic |
|---|---|
| YAML cannot be safely parsed, including duplicate YAML mapping keys | Existing `YAML_PARSE_ERROR` |
| Missing/ambiguous dependency snapshot, package identity, trusted Owner binding or Owner mismatch | Existing `DEPENDENCY_*` diagnostic, including `DEPENDENCY_EXPORT_OWNER_UNVERIFIED` and `DEPENDENCY_OWNER_MISMATCH` |
| Catalog shape, kind or apiVersion invalid/unsupported | `INGRESS_CATALOG_INVALID` |
| Duplicate `operations[].id` | `INGRESS_EXPORT_ID_DUPLICATE` |
| Duplicate exact `event.source + event.service + event.operation` tuple | `INGRESS_EVENT_SELECTOR_DUPLICATE` |
| Trigger ToolCatalog Operation missing/ambiguous after exact Package ID and Owner scoping | Existing `EXPORT_ID_MISSING` / `EXPORT_ID_AMBIGUOUS` |
| OpenAPI source bytes or dependency identity/digest untrusted or mismatched | Existing dependency identity diagnostic; do not emit a protocol metadata diagnostic |
| Trusted OpenAPI artifact has inconsistent release, API URI version, method, path or operationId metadata | `INGRESS_PROTOCOL_ARTIFACT_INVALID` |
| Source, normalized, arm-input or response Schema missing/invalid, or Schema Closure resolution invalid | Existing `SCHEMA_MISSING` / `SCHEMA_INVALID` |
| Ingress-owned peer profile reference malformed or unresolved in the declared trusted snapshot | `INGRESS_PEER_PROFILE_REFERENCE_INVALID` |
| Request normalization declaration/mapping invalid | `INGRESS_NORMALIZATION_INVALID` |
| Ingress-owned correlation, duplicate identity or stale-delivery declaration invalid | `INGRESS_CORRELATION_INVALID` |
| Selected Skill cannot materialize its `armInputSchema` or prove path-specific stale-delivery safety | CA-SL `WAIT_CORRELATION_BINDING_INVALID` |
| Ingress-owned response mode, deadline, disposition, failure-response or recovery contract invalid | `INGRESS_RESPONSE_CONTRACT_INVALID` |
| Ingress-owned response representation or protocol response mapping invalid | `INGRESS_RESPONSE_MAPPING_INVALID` |
| Skill `response.after` missing/unreachable | CA-SL `WAIT_RESPONSE_BOUNDARY_INVALID` |
| Skill Producer-to-response mapping invalid | CA-SL `WAIT_RESPONSE_MAPPING_INVALID` |
| Wait selector matches zero/multiple trusted Ingress exports | CA-SL `WAIT_INGRESS_EXPORT_NOT_FOUND` / `WAIT_INGRESS_EXPORT_AMBIGUOUS` |

This table is exhaustive for the current IngressCatalog v1alpha1 static diagnostic ownership boundary. The following former candidates are deliberately not Ingress diagnostics: `INGRESS_OWNER_UNVERIFIED`, `INGRESS_REQUEST_SCHEMA_INVALID`, `INGRESS_TRIGGER_OPERATION_NOT_FOUND`, `INGRESS_TRIGGER_OPERATION_AMBIGUOUS`, `INGRESS_TRIGGER_BINDING_INVALID`, and `INGRESS_STALE_DELIVERY_UNSAFE`. Their conditions are owned by the existing dependency, Schema, export-link, SourcePath, Wait-correlation or Ingress-correlation diagnostics above.

## 4. Deterministic precedence and cascade suppression

The Compiler MUST apply the following prerequisite order to a single Catalog dependency:

1. Safe YAML parse. A parse failure emits `YAML_PARSE_ERROR`; no Catalog semantic diagnostic is inferred from the unparsed document.
2. Dependency snapshot, Package ID, trusted identity and Owner binding. If this prerequisite fails, emit the existing dependency diagnostic(s) and suppress all Ingress registry diagnostics for the affected untrusted snapshot.
3. Catalog root shape, `kind` and `apiVersion`. If `INGRESS_CATALOG_INVALID` makes the Catalog unparseable as this contract, suppress operation-level Ingress diagnostics for that Catalog.
4. Export ID and exact event-selector uniqueness. Independent duplicate constraints MAY both be reported; each duplicate is anchored to the later occurrence.
5. Exact ToolCatalog trigger Operation linking. Use existing `EXPORT_ID_MISSING` / `EXPORT_ID_AMBIGUOUS`; do not translate these to Wait selector diagnostics.
6. Source artifact identity/digest and Schema resolution. Dependency identity errors precede protocol metadata checks; `SCHEMA_MISSING` / `SCHEMA_INVALID` precede normalization or response mapping errors that depend on the unresolved Schema.
7. Trusted OpenAPI protocol metadata, peer-profile references and request normalization.
8. Ingress-owned correlation and stale-delivery declaration.
9. Ingress-owned response contract, then response representation/mapping.
10. Skill-specific Wait selector, path/correlation, response boundary and Producer mapping checks.

The numeric `precedence` values in the machine registry order the Ingress-owned entries within this dependency order. When multiple independent errors remain at the same precedence, the Compiler MUST sort by dependency alias, snapshot path, JSON Pointer and Code using unsigned UTF-8 byte order. It MUST NOT emit downstream diagnostics whose required prerequisite failed. This prevents one untrusted Owner, invalid Catalog root or unresolved Schema from producing a cascade of misleading Ingress errors.

## 5. Registry entries

The machine-readable registry is normative for exact Codes, Phase, Severity, build-blocking behavior, precedence, message keys, templates and source-location policies. The nine entries are:

| Code | Phase | Severity | Blocks Build | Precedence | Message key | Conformance |
|---|---|---|---|---:|---|
| `INGRESS_CATALOG_INVALID` | C_STATIC | ERROR | Yes | 10 | `ingress.catalog.invalid` | IN-055 |
| `INGRESS_EXPORT_ID_DUPLICATE` | C_STATIC | ERROR | Yes | 20 | `ingress.export.id.duplicate` | IN-005 |
| `INGRESS_EVENT_SELECTOR_DUPLICATE` | C_STATIC | ERROR | Yes | 21 | `ingress.event.selector.duplicate` | IN-056 |
| `INGRESS_PROTOCOL_ARTIFACT_INVALID` | C_STATIC | ERROR | Yes | 30 | `ingress.protocol.artifact.invalid` | IN-057 |
| `INGRESS_PEER_PROFILE_REFERENCE_INVALID` | C_STATIC | ERROR | Yes | 40 | `ingress.peer.profile.reference.invalid` | IN-058 |
| `INGRESS_NORMALIZATION_INVALID` | C_STATIC | ERROR | Yes | 50 | `ingress.normalization.invalid` | IN-059 |
| `INGRESS_CORRELATION_INVALID` | C_STATIC | ERROR | Yes | 60 | `ingress.correlation.invalid` | IN-060 |
| `INGRESS_RESPONSE_CONTRACT_INVALID` | C_STATIC | ERROR | Yes | 70 | `ingress.response.contract.invalid` | IN-061 |
| `INGRESS_RESPONSE_MAPPING_INVALID` | C_STATIC | ERROR | Yes | 80 | `ingress.response.mapping.invalid` | IN-062 |

## 6. Version boundary

This registry is a candidate normative companion to IngressCatalog v1alpha1. It does not modify the frozen CA-SL v1alpha4 diagnostic index. CA-SL v1alpha5 Appendix H composes these identities into its unified review index while preserving this registry as their versioned owner. Until the IngressCatalog contract and registry are independently frozen and released, no Compiler implementation or product-conformance claim follows from this document.
