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

The machine-readable vector is [schema-closure-digest-v1.vector.json](schemas/schema-closure-digest-v1.vector.json). It covers a root Schema that references a Schema in a second artifact. Implementations MUST produce the same digest when the input node list is supplied in a different order, and MUST produce a different digest when a referenced Schema node or its artifact identity changes.

