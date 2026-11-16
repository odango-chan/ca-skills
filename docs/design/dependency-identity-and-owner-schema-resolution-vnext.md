> **Status notice (2026-11-14):** Non-normative implementation-boundary note. The CA-SL v1alpha4 language/interop contract is frozen; concrete external BuildRequest transport and Owner deployment artifacts remain separately versioned. The comprehensive [CA-SL vNext Specification](../skill-language-spec.v1alpha4.zh-CN.md) is the sole normative source for language and dependency identity semantics. This note records implementation boundaries and unresolved deployment inputs; the current normative ToolCatalog / CapabilityContracts interoperability profile is now in Appendices F and G of the canonical spec.

# Dependency Identity & Owner Schema Resolution — Skill Language vNext

**Status:** Implementation guidance only; CA-SL language frozen, external toolchain and Owner conformity pending (2026-11-14).
**Scope:** `ca-skills`, Skill Studio Plugin-managed Configuration, `ca-skill-compiler`, and the executable conventional 5GC Skill.

This note records an earlier cross-repository implementation boundary. The canonical [CA-SL v1alpha4 specification](../skill-language-spec.v1alpha4.zh-CN.md) is now the frozen language authority. Older DESIGN-REVIEW proposals in this file do not override that contract; BuildRequest transport and real Owner releases still require their independent conformance gates.

## 1. Decisions

1. Skill source never names a physical workspace path such as `lib/host/subject.schema.yaml`.
2. Skill source references imported Tool Operations, Observation Tool query contracts and Owner Schemas by `<dependency-alias>::<exact-exported-id>`.
3. The alias is a logical namespace mapped by Plugin-managed Workspace Configuration to one supplied dependency snapshot. It is not a repository URL, local path, source kind, revision, digest, cache key or acquisition instruction.
4. Studio owns dependency selection, acquisition, immutable snapshot persistence, locking, refresh and cache. Compiler receives the exact bytes and does not acquire or manage them.
5. Compiler BuildRequest contains Skill source files and immutable dependency snapshots. The trusted caller also provides Package ID / Owner bindings for those snapshots and separate deployment CapabilityContracts (§34.0).
6. Capability IDs in `capabilities` are unqualified exact IDs from that single trusted CapabilityContracts input. Tool/Schema aliases do not qualify or own deployment authorization.
7. Compiler links each exact callable contract (Operation or Observation query) to exactly one Capability and cross-checks its ToolCatalog Effect against the independently declared Capability Effect. Runtime repeats authorization and Effect admission.
8. No project manifest, lockfile, package resolver, Compiler dependency digest output, or physical `lib/` source layout is introduced.
9. vNext is a breaking replacement. The Compiler rejects v0.2 `lib/**` paths, direct callable grants and Predicate-owned Observation declarations. Observation query contracts are imported through ToolCatalog; no compatibility parser or field mapping remains.
10. For the frozen CA-SL v1alpha4 migration described by this note, Skill-level `wait`, `await` and polling nodes are not part of the language. Asynchronous protocol/service completion is encapsulated by the owning Tool/SMF Operation; Host deadlines/cancellation remain Runtime controls. This is a v1alpha4 rule, not a decision on a later language revision. The separate post-v1alpha4 Node-entry Event Wait proposal is tracked in [Draft PR #60](https://github.com/odango-chan/ca-skills/pull/60) and MUST NOT be applied to v1alpha4 source.

## 2. Compiler input boundary

The caller supplies all source bytes required for one build. Reuse the existing v0.1 snapshot shape:

```typescript
type File = { path: string; bytes: Uint8Array };

type DependencySnapshot = {
  dependencyId: string; // Workspace alias
  digest: string; // verified against canonical snapshot bytes
  files: File[]; // paths are relative to this snapshot
};

type BuildRequest = {
  files: File[]; // Skill source only, under skills/**
  resolvedDependencies: DependencySnapshot[];
  capabilityContracts: File; // trusted deployment composition, separate input
  targets?: string[];
};
```

The sketch reuses the v0.1 snapshot fields. The vNext transport for trusted Package ID and Owner bindings is pending; the caller supplies them keyed by alias and verified digest. Compiler validates paths, bytes, digest, identity and exact exports. See CA-SL §34.0.

BuildResult returns diagnostics and generated Skill-owned output files. It does not export dependency digests or copy dependency snapshots into generated Skill source. Studio owns dependency lock and persistence.

## 3. Imported contract identity

- Operation call: `fivegc-tools::sbi.udm.sm_data.get`
- Observation query: `fivegc-observations::ue.registration.current`
- Host Subject Schema: `ca-context::urn:connectionagent:ca:context:subject:v1` (3GPP `supi` only)
- Capability grant: `provider-5gc.createdsession.udm`

The alias selects the exact caller-supplied snapshot. The exported ID remains Owner-defined. Resolve the export uniquely within the selected snapshot; enforce any additional Schema or Capability identity uniqueness constraints during linking.

CapabilityContracts is not a normal dependency snapshot. It is deployment-owned trusted input. The Skill may grant a Capability ID but cannot define its owner, callable membership (Operations and Observation queries), Effect or budget policy.

## 4. Tool and Observation contract inventory

The current executable deployment baseline has six Capability groups and twelve Operations. This is the legacy Operation inventory, not the final vNext callable-contract total.

Observation query contracts are not inferred one-for-one from Operations:
- an Observation Tool is a specialized read-only Tool contract using the same ToolCatalog, dependency snapshot, Owner Schema, CapabilityContracts and Runtime admission model;
- an Observation Tool may expose one or more exact query identities;
- one Mutation Operation does not imply a paired Observation query;
- an Operation output may be consumed directly when it already supplies the exact value and correlated Evidence;
- independent Observation queries are added only where the Agent/Procedure needs additional authoritative context.

The current 17 legacy 5GC Predicate Observation refs are migration inputs, not 17 mandatory new query Tools or READ Operations. The 2026-11-16 context boundary supersedes their old access plan: Host ingress/journal facts remain private; prior Operation values are consumed from the exact Operation Result; non-SMF reads remain inside their responsible Tool; only exact SMF MAS-owned projections may become direct Agent Observations. In particular, raw N4/UPF resource and RAN setup snapshots must not be relabelled as UPN/SSM facts by name similarity. The historical source-backed classification was:
- 1 captured ingress projection from Host Invocation Context;
- 9 prior-Operation/local projections;
- 2 Host journal projections;
- 5 independent query points across four Observation Tool query shapes (N4 baseline, post-create N4 resources, RAN setup, N4 forwarding, PCF governance).

The exact vNext Observation Tool query identities, schemas and Capability membership must be derived from the Owner-published ToolCatalogs and the 17-ref migration mapping. Do not maintain a speculative aggregate Operation count here. In particular, the three legacy `ca.session.evidence.await` nodes are removed from the Skill model; their asynchronous completion responsibilities move inside `UPN.CREATE_UP_SESSION`, `SSM.SIGNAL_UE_AN` and `UPN.MODIFY_UP_SESSION`. There is no v1alpha4 Skill-level Wait Tool or polling contract. This migration statement does not pre-judge the separate post-v1alpha4 Event Wait proposal in [Draft PR #60](https://github.com/odango-chan/ca-skills/pull/60).

## 5. Evidence and prior-operation results

An Observation Tool returns its normalized value and declared Evidence guarantees. A Predicate consumes explicitly bound values through positional `precondition.arguments` or `postcondition.arguments`. Compiler and Runtime verify `evidence.requires` as described in CA-SL §17.

For UDM Get:

- the Provider Owner Schema validates the upstream HTTP response inside Host;
- the Host adapter's normalized `CreatedSessionUDMResult.runtime_value()` needs its own exported Schema;
- ToolCatalog `outputSchema.result` references the Host projection Schema, not the Provider wire Schema;
- Predicate receives the exact `nudm-sdm-get.output.result` and Evidence from the same full Provider receipt;
- no second UDM Get or parallel `sbi.operation.result` acquisition is allowed.

For local projections over hold, operation-context, PCF input, resource-ownership and AMF transfer results, reuse the exact stored artifact. Do not synthesize a `CURRENT` binding status from a handle or mutation success alone. Preserve selector, lifecycle, deadline, transaction, freshness and evidence checks.

## 6. 5GC-first acceptance

1. Use the Host-owned subject-only Context Schema (3GPP `supi`) and the Host Evidence-reference projection; keep ingress/lifecycle/invocation metadata in the separate private Host execution context.
2. Keep the Host private execution-context Schema separate from Skill `contextSchema`; the current proposed export is an internal Host-to-Tool contract, not a normal Skill dependency. Publish typed Tool Output Schemas for all current Operation outputs consumed by Predicates.
3. Publish exact SMF MAS Observation Tool query contracts only for SMF-owned facts still required after direct Operation-output and Subject Context reuse is proven. Non-SMF context stays inside the responsible Tool; do not expose cross-NF Agent query surfaces.
4. Update the trusted CapabilityContracts map and ToolCatalog together for both Operations and Observation query identities; fail closed on missing/duplicate membership or Effect mismatch.
5. Migrate the conventional 5GC Skill to pure Predicate inputs and explicit Observation Tool queries where needed; do not add Skill-level Wait/polling.
6. Build the 5GC Skill using supplied dependency snapshots without any physical `lib/` folder.
7. Validate the existing 36 Cases and three References as unchanged business constraints, then run focused Compiler/Runtime/5GC acceptance.

MAS remains non-executable design material and is not a prerequisite for 5GC acceptance.


## 7. 2026-11-16 SMF-only context access decision

The SMF MAS QueryContext SBI v0.10 design is an implemented external baseline, not a new schema-authoring task for ca-skills. The separate `ca-5gc-client-tools` package provides eight separately typed read-only query callables; the Host only supplies trusted subject/lifecycle context and dispatch. Skill source references only exact Host/Owner exports after publication; it never embeds SBI paths, static tokens, SUPI/IMSI lookup keys or private lifecycle/correlation values.

The reserved dependency Package IDs are:
- `ca-context`: `urn:connectionagent:ca:host-context` (subject-only Context Schema package);
- `smf-mas-observations`: `urn:connectionagent:ca:5gc:smf-mas-observations` (eight SMF MAS Observation callable/schema package owned by `ca-5gc-client-tools`).

Both IDs are reserved identities, not published dependency snapshots or trusted Owner bindings. The two example Skills use only the `ca-context` subject projection and do not call the eight Observation tools. Do not add `smf-mas-observations` to either Skill until a Procedure actually references one of its callables.

HostBusinessCorrelation is a Host-owned private payload containing only `ingressRef` and `lifecycleRef`. The Host supplies the stable Runtime Execute `requestId`; ca-runtime owns its `(host, requestId)` RequestStore, fingerprint, deduplication and replay authority. Runtime generates `runId`, `invocationId`, Action/Node occurrence identity and `dispatchAttemptId`, and resolves `environmentRef`. The proposed RuntimeHost `hostBusinessCorrelation` transport extension is not yet in RuntimeHost.v1; no merged physical Host/Runtime envelope Schema is published. Host persistence is limited to ProductTask, AgentInstance, HostBusinessInstance, ingress admission/deduplication and request-ledger/transport continuity. ca-runtime owns RunRecord/RunEvent, Procedure progression, Action outcome, Evidence and Reconcile; Provider/Owner owns protocol transactions, callbacks, waiter/hold/claim/journal records and resource receipts. The Skill-visible Subject Context remains separate.

The `ca-5gc-client-tools` ToolCatalog is an Owner dependency snapshot used for CA-SL linking. It is not a second Server Tool Catalog. The existing `tool-mcp-gw` Server Tool Catalog and Runtime Resolved CA Toolset / Capability authorization / Admission path remain authoritative. The Host-local adapter registry is an implementation binding, not a grant or catalog.

The eight callable exports use reserved DottedId Guarantee names (`smf.mas.<mas>.context.query-evidence`). The Evidence Descriptors are not publishable until the SMF Owner provides an exact stable authority identity and closes the temporal guarantee. The per-MAS Scope policy names are deployment-owned references; the corresponding trusted policy bodies and grants are not published. CapabilityContracts remains a separate deployment-owned BuildRequest input; each Capability is deployment-owned and each callable member is owned by `ca-5gc-client-tools`.

The wire response exposes `masId/status/key/context`. `AVAILABLE` means the MAS State has been authoritatively written, not that the value is fresh or that the complete PDU Session is established. `UNAVAILABLE` is an empty projection for an existing UE/session whose MAS State is not written; it is not false. `SESSION_NOT_FOUND` remains a distinct 404.

The v0.10 response does not carry source time or Host lifecycle identity. Host `queryStartedAt` and `receivedAt` are audit timestamps, not source `observedAt`. Host/SMF must publish the missing temporal/freshness and exact UE/PSI/lifecycle Evidence binding before any of these callables can qualify under CA-SL v1alpha4. Do not invent `observedAt` from Host receipt time.

The complete 17-reference legacy source mapping is recorded in the [Legacy CreatedSession Observation Crosswalk](https://github.com/odango-chan/ca-agent-demo/blob/docs/5gc-agent-context-boundary-20261116/docs/5gc-legacy-observation-crosswalk-v1alpha4.md). The current example Skill source still contains placeholder identities for its non-Host Tool packages and Capabilities; the reserved Host Package ID alone does not make either Skill linkable or qualified.
