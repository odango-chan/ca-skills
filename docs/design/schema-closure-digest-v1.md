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

Closure discovery is part of this algorithm's conformance, not an implementation-defined pre-step.

- `artifactRef` is an opaque, exact identity assigned by the trusted dependency-snapshot resolver to one artifact in the immutable BuildRequest snapshot. It MUST be bound one-to-one to that artifact's normalized snapshot-relative path and canonical document URI by the same pinned dependency resolver used for trusted dependency linking. It MUST NOT be inferred from a filename, dependency alias, OpenAPI `operationId` or network URL. The path/URI binding MUST be covered by the trusted dependency snapshot and Owner binding used by the Build.
- The root `schemaRef` MUST first resolve through the exact trusted Schema export binding to one `(artifactRef, pointer)`. No name search, fallback path, floating registry lookup or version negotiation is allowed.
- For an OpenAPI 3.0 source Schema, a relative `$ref` is resolved as an RFC 3986 URI-reference against the canonical document URI of the containing OpenAPI artifact. For a JSON Schema Draft 2020-12 Schema, the effective base URI follows the dialect's `$id` rules, then RFC 3986 URI-reference resolution is applied. Any effective base URI / alias MUST resolve through the same immutable snapshot resolver; it MUST NOT trigger network retrieval.
- After URI resolution, the document URI MUST map to exactly one `artifactRef` in the same trusted dependency closure. An unmapped or ambiguous URI, an attempt to escape the snapshot, or a target outside the declared closure is rejected.
- A reference fragment MUST be empty (the target document root) or a JSON Pointer fragment. The resolver percent-decodes the URI fragment exactly once, validates RFC 6901 escaping, and canonicalizes it to `#` for the root or `#/` followed by canonical JSON Pointer tokens (`~` encoded as `~0`, then `/` encoded as `~1`). This canonical decoded pointer is the `pointer` value included in the digest manifest. Equivalent percent-encoded fragment spellings therefore identify the same Schema node.
- Named anchors, `$anchor` references, `$dynamicRef`, `$dynamicAnchor` and `$recursiveRef` are not supported by Schema Closure Digest v1 and MUST fail closed. A future algorithm may add them under a new algorithm identifier.
- The resolved pointer MUST identify a Schema node valid under the containing artifact's declared dialect. References to non-Schema OpenAPI objects or arbitrary non-Schema JSON values are rejected.

The resolver's artifact-URI map and the source `$ref` strings are inputs to closure discovery, but are not additional fields in the JCS manifest. The manifest binds the resulting exact artifact identities, pointers, source artifact digests and parsed Schema values. The machine vector includes a separate resolution context to test this discovery step; that context is not hashed.


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

The machine-readable vector is [schema-closure-digest-v1.vector.json](schemas/schema-closure-digest-v1.vector.json). It covers a root Schema that references a Schema in a second artifact and includes the canonical artifact-URI map / reference-resolution expectation. Implementations MUST prove that the relative `$ref` resolves to the exact target `(artifactRef, pointer)` in the closure, produce the same digest when the input node list is supplied in a different order, and produce a different digest when a referenced Schema node or its artifact identity changes. The resolution context is test input only and is not part of the JCS digest manifest.

