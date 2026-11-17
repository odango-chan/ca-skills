# Schema Closure Digest v1

**Status:** Proposed companion algorithm for IngressCatalog v1alpha1. It is independent of the CA-SL language version and does not replace the BuildRequest dependency-snapshot digest.

## 1. Purpose and identity

IngressCatalog references Schema resources that may be embedded in OpenAPI artifacts and may transitively reference schemas in other pinned artifacts. A file-set digest alone proves the complete dependency snapshot, but it does not identify the exact Schema root selected by a `schemaRef`.

The Schema Closure Digest binds one exact Schema root to the complete set of Schema nodes reachable through its references.

The algorithm identifier is `connectionagent.io/schema-closure/v1`. Its binary domain separator is the ASCII byte sequence:

```text
CA-SKILL-SCHEMA-CLOSURE\0v1\0
```

The wire value is `sha256:` followed by 64 lowercase hexadecimal characters.

## 2. Root resolution and closure

Before computing the digest, the trusted Schema resolver MUST resolve the exact `schemaRef` to one root identity:

- `artifactRef`: the exact artifact identity in the declared immutable dependency snapshot;
- `artifactDigest`: the SHA-256 digest of the complete source artifact bytes;
- `pointer`: a JSON Pointer fragment identifying the Schema node within that artifact (`#` or a fragment beginning with `#/`).

The resolver MUST follow every `$ref` reachable from the root Schema node, including references nested in properties, items, compositions and other Schema substructures supported by the source dialect. Every target MUST resolve to an artifact in the same explicitly declared trusted dependency closure. Network retrieval, floating URLs, undeclared files and resolver fallback are forbidden.

### 2.1 Deterministic reference resolution

Closure discovery is part of this algorithm's conformance, not an implementation-defined pre-step. The trusted dependency resolver MUST provide, for every artifact in the declared closure:

- its exact `artifactRef`;
- its normalized, snapshot-relative `snapshotPath`;
- its canonical `documentUri`;
- its source Schema dialect (`openapi-3.0` or `json-schema-2020-12`);
- the exact complete raw source-artifact bytes;
- the parsed document derived from those same bytes.

The resolver MUST compute `artifactDigest = SHA-256(raw source-artifact bytes)` itself. It MUST NOT trust a digest supplied by IngressCatalog, a caller, or a pre-resolved vector. The parsed document used for Schema discovery MUST be produced from those exact bytes by the parser for the declared source format. A separately supplied parsed document that does not equal the parse result MUST be rejected. This binds byte identity and parsed Schema identity to one immutable snapshot object; a formatting/comment-only source change therefore changes the artifact digest even when the selected Schema value is unchanged.

The resolver MUST bind `artifactRef`, `snapshotPath` and `documentUri` one-to-one. The canonical `documentUri` MUST be derived by resolving the percent-encoded `snapshotPath` against the immutable snapshot base URI. The snapshot base URI MUST be absolute, hierarchical and end in `/`. A snapshot path MUST be relative and normalized; empty segments, `.`, `..`, leading slash and backslash are rejected.

A canonical document URI MUST be absolute and hierarchical, contain no user-info, query or fragment, and use a lowercase scheme and host. Default HTTP/HTTPS ports are removed, dot segments are removed, percent-encoded unreserved characters are decoded, and remaining percent escapes use uppercase hexadecimal. Whitespace, backslashes, malformed percent escapes and repeated path separators are rejected. URI resolution is an allowlisted identity lookup only: the resolver MUST NOT perform network retrieval.

- `artifactRef` is an opaque, exact identity assigned by the trusted dependency-snapshot resolver. It MUST NOT be inferred from a filename, dependency alias, OpenAPI `operationId` or network URL.
- The root `schemaRef` MUST first resolve through the exact trusted Schema export binding to one `(artifactRef, pointer)`. No name search, fallback path, floating registry lookup or version negotiation is allowed.
- For an OpenAPI 3.0 source Schema, a relative `$ref` is resolved as an RFC 3986 URI-reference against the canonical document URI of the containing OpenAPI artifact. OpenAPI 3.0 Schema Objects do not use `$id` to establish a base URI; a reachable `$id` in such a Schema Object MUST be rejected.
- For a JSON Schema Draft 2020-12 source Schema, the effective base URI follows the nearest enclosing `$id` rule. Each `$id` MUST be a non-empty URI-reference without a fragment. It is resolved against the inherited base URI and registers an immutable resource-URI alias to the exact `(artifactRef, resourcePointer)` where that `$id` occurs. A conflicting alias, an alias that cannot be bound to exactly one artifact/resource pointer, or an invalid `$id` MUST fail closed.
- A relative or absolute `$ref` is resolved against the effective base URI of the Schema Object that contains it. The resolved document/resource URI MUST map either to one canonical document URI or to one registered JSON Schema `$id` alias in the same trusted dependency closure. An unmapped URI, an ambiguous alias, an attempt to escape the snapshot, or a target outside the declared closure is rejected. No URI may trigger network access.
- The fragment MUST be empty or a JSON Pointer fragment. The resolver percent-decodes the URI fragment exactly once as strict UTF-8, validates RFC 6901 token escaping, and canonicalizes it to `#` or `#/` followed by canonical JSON Pointer tokens (`~` encoded as `~0`, then `/` encoded as `~1`). A fragment pointer is relative to the selected resource root; when the resource is a nested `$id`, its tokens are appended to that resource's artifact-relative `resourcePointer`. The resulting artifact-relative pointer is the `pointer` stored in the digest manifest. Equivalent percent-encoded fragment spellings therefore identify the same Schema node.
- The resolved pointer MUST identify an actual Schema Object under the containing artifact's declared dialect. For OpenAPI 3.0, only Schema Object locations and their nested Schema-valued keywords are eligible. For JSON Schema Draft 2020-12, only the root Schema and Schema-valued keyword locations are eligible. Boolean Schemas are not supported by Schema Closure Digest v1. References to arbitrary JSON values, non-Schema OpenAPI objects or missing pointers are rejected.
- Named anchors, `$anchor`, `$dynamicRef`, `$dynamicAnchor` and `$recursiveRef` are not supported by Schema Closure Digest v1 and MUST fail closed. A future algorithm may add them under a new algorithm identifier.

The resolver MUST traverse every reachable `$ref` within Schema-valued substructures supported by the declared dialect, including nested properties, items, compositions and definitions. Recursive/cyclic references are visited once per exact `(artifactRef, pointer)` identity. The resulting closure MUST contain every and only the root plus all transitive `$ref` target Schema nodes. Missing and extra nodes are invalid.

The resolver's snapshot-path map, canonical document-URI map, JSON Schema `$id` aliases and source `$ref` strings are inputs to closure discovery, but are not additional fields in the JCS manifest. The machine vector includes complete parsed documents, their snapshot-path/URI/dialect bindings and a nested-`$id` transitive reference case to test discovery. That resolution context is not hashed.

Each distinct resolved Schema node is identified by the pair `(artifactRef, pointer)` and MUST appear exactly once in the closure. The root node MUST be included. Recursive/cyclic references are permitted in the graph and MUST be visited once per identity; they MUST NOT cause unbounded traversal.

Each node's `schema` value is the exact parsed JSON-compatible object at that pointer. YAML/JSON parsing MUST reject duplicate mapping keys, non-string object keys, unsupported custom tags, non-finite numbers and values that cannot be represented as JSON. The original `$ref` strings remain unchanged in the node value; the corresponding resolved target node is also included in the closure.

The algorithm does not rewrite OpenAPI 3.0 Schema Objects into JSON Schema Draft 2020-12, or vice versa. Canonicalization is a representation rule only; validation semantics continue to follow the exact source artifact's declared dialect.

## 3. Canonical manifest

Construct the following JSON object:

```json
{
  "algorithm": "connectionagent.io/schema-closure/v1",
  "root": {
    "artifactRef": "<exact artifact identity>",
    "artifactDigest": "sha256:<64 lowercase hex>",
    "pointer": "#/components/schemas/Example"
  },
  "nodes": [
    {
      "artifactRef": "<exact artifact identity>",
      "artifactDigest": "sha256:<64 lowercase hex>",
      "pointer": "#/components/schemas/Example",
      "schema": {}
    }
  ]
}
```

The `nodes` array MUST contain exactly the root's transitive Schema-reference closure and MUST be sorted by unsigned lexicographic order of UTF-8 `artifactRef` bytes, then unsigned lexicographic order of UTF-8 `pointer` bytes. Duplicate node identities are invalid. The `root` object MUST exactly identify one entry in `nodes`.

Serialize the complete manifest using JSON Canonicalization Scheme (JCS), RFC 8785. No whitespace, trailing newline, YAML serialization, URI rewriting, key omission or additional fields are inserted.

## 4. Digest calculation

The digest is:

```text
SHA-256(
  ASCII("CA-SKILL-SCHEMA-CLOSURE\0v1\0")
  || JCS(manifest)
)
```

The result is encoded as `sha256:<lowercase hex>`.

The algorithm applies to every IngressCatalog field that carries a `schemaDigest` or `responseSchemaDigest`, including source request Schemas, normalized request Schemas, multipart JSON part Schemas and response representation Schemas. The resolved root and closure MUST be computed from the exact trusted dependency snapshot used by the Build.

## 5. Relationship to dependency snapshot identity

The BuildRequest dependency-snapshot digest remains authoritative for the complete immutable file set, paths and raw file bytes. Schema Closure Digest is a narrower projection that identifies one Schema root and its reachable Schema graph. It is not a package identity, trust statement, publication signature or substitute for Owner verification.

The complete artifact digest is included for every closure node. Therefore, changing any byte in an artifact that contains a referenced Schema changes the Schema Closure Digest, even if the selected node's parsed value is unchanged. This conservative rule avoids treating a changed OpenAPI artifact as the same published Schema source.

A successful digest check does not establish that the Schema is valid for a protocol, that an Owner is trusted, or that a deployed Integration Adapter conforms. Those checks remain separate.

## 6. Golden vector

The machine-readable vector is [schema-closure-digest-v1.vector.json](schemas/schema-closure-digest-v1.vector.json). It includes an OpenAPI 3.0 root, a JSON Schema Draft 2020-12 dependency with a nested relative `$id`, and a further transitive `$ref` whose fragment is relative to a non-root nested resource and must translate to the exact artifact-relative pointer `#/$defs/Shared/$defs/Leaf`. Each resolution-context document carries its exact `rawArtifact` UTF-8 source bytes; the fixture uses compact JSON text, which is also valid YAML 1.2, so the validator can parse the same bytes and compare them with the supplied parsed document. The validator recomputes each artifact digest from those bytes. It does not accept a caller-supplied list of already-resolved edges or digest values as proof. Implementations MUST prove exact artifactRef/path/document-URI/raw-byte binding, dialect-aware base resolution, nested-resource fragment translation, exact reachable-node closure, input-order-independent digest calculation, rejection of stale declared digests, and a changed closure digest when raw artifact bytes change while parsed Schema values remain identical. The resolution context and raw source bytes are test inputs only and are not part of the JCS digest manifest.

