# Gateway-owned Business Resource Identity

**Status: Accepted**
**Version: 1**
**Date: 2026-10-01**
**Tracking: odango-chan/ca-agent#15, odango-chan/ca-skills#7**
**Canonical ID rule: `odango-chan/connectionagent@main:docs/architecture/identity-association.md`**

## 1. Purpose

This contract freezes the lifecycle of gateway-owned business resource identifiers
used by the governed 5GC file-transfer path, starting with `transferId`. It answers
who owns the identifier, when it is allocated, how it survives retry / UNKNOWN /
reconcile, how it enters the executable Skill input, how independent observation
queries by it, and what ConnectionAgent components must never do with it.

It is a business/domain contract owned by `ca-skills`. It does not introduce a new
cross-repository runtime service, global correlation object, or Evidence identity.

## 2. Ownership

```text
transferId owner = the external business gateway
                   (the file-transfer application that initiates the operation)
```

The gateway allocates `transferId` when it initiates a transfer, persists it in its
transfer record, and supplies it with the business request. No ConnectionAgent
component allocates it: not the Agent Host, not the Runtime, not the Provider, not
the Benchmark Engine.

ConnectionAgent owns only **admission and preservation** of the gateway-supplied
value:

```text
gateway business request
  -> 5gc-intent request (this repository: skills/5gc-intent/schemas/5gc-intent-request.schema.yaml)
  -> Agent routing / planning (preserve, never re-derive)
  -> 5gc-file-transfer executable request (this repository: skills/5gc-file-transfer/schemas/file-transfer-request.schema.yaml)
  -> Provider mutation (domain operation keyed by transferId)
  -> owner evidence / independent observation (queried by the same transferId)
```

When the business request is already classified (`[TASK: 5GC-FILE-TRANSFER]`) or no
Agent Host participates (`RUNTIME_ONLY`), the same gateway-supplied value enters
through the corresponding Goal / executable request material. The composition path
must not change ownership or allocation rules.

## 3. Lifecycle

```text
allocation timing
  before the business request reaches ConnectionAgent; the gateway owns the transfer
  record from that point on.

supply field
  5gc-intent request: `transferId` (optional; required whenever the routed target
  requires transfer correlation)
  5gc-file-transfer request: `transferId` (required)

persistence
  gateway transfer record. ConnectionAgent retains only refs/digests/provenance.

same logical mutation retry
  reuse the same transferId. The provider mutation is idempotent with respect to it.

OUTCOME_UNKNOWN / reconcile
  reuse the same transferId. A reconcile query is keyed by that transferId; it is not
  a new business resource and must not allocate a replacement identifier.

protocol / reliability identity
  requestId, callId, RuntimeRequestId, RuntimeRunId, Tool call ids and Benchmark
  Attempt/Trial ids may change between attempts. They never substitute for transferId.

independent observation
  `virtual_group.snapshot` and equivalent owner observations are queried by the same
  transferId, in the same prepared Environment generation.

return path (owner evidence)
  the mutation result and the independent observation both carry the transferId they
  were executed/observed under, so a consumer can prove they concern the same
  business resource without any Benchmark or Runtime identity being forwarded.
```

## 4. Prohibited aliases

```text
transferId != BenchmarkRunRef
transferId != EvaluationTaskRef
transferId != TrialRef
transferId != AttemptRef
transferId != ProductTaskRef
transferId != AgentInstanceRef
transferId != RuntimeRequestId / requestId
transferId != RuntimeRunId / runId
transferId != callId
transferId != EnvironmentInstanceId
```

Deriving `transferId` from a routing `requestId`, a Benchmark orchestration id, a
Runtime run id, or an Environment identity is non-conforming and must fail closed.

## 5. Composition independence

```text
LLM_RUNTIME
LLM_ONLY
RUNTIME_ONLY
```

All three must use the same owner and the same allocation/supply rule for the same
business operation. In particular, `RUNTIME_ONLY` must not cause the Benchmark (or
any other component) to synthesize a transferId merely because no Agent Host
participates.

Where a benchmark consumes source-owned business request material, that material
carries the gateway-issued value; the Benchmark retains a materialization
provenance record (source ref, digest, owner revision, association) and never
generates the identifier at runtime.

## 6. What each component must do

```text
gateway
  allocate, persist, resend the same transferId on retry/reconcile.

Agent Host / routing (LLM_RUNTIME, LLM_ONLY)
  preserve the gateway-supplied transferId into the selected Skill input;
  do not allocate it; do not derive it from requestId; do not use a Trial/run id.

deterministic materialization (RUNTIME_ONLY and non-Agent paths)
  copy the source-owned gateway value into the executable request unchanged;
  fail closed when it is absent.

governed execution / Provider
  key the domain mutation by the supplied transferId; do not invent one.

evidence / observation owners
  key observations by the same transferId and expose it in owner-native results.

Benchmark / evaluator
  associate externally (for example `Attempt --MATERIALIZED_RESOURCE--> transferId`)
  and retain provenance; never forward Trial/Benchmark identity into the DUT request.
```
