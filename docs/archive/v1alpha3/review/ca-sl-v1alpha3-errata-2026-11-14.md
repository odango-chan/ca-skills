# CA-SL vNext / v1alpha3 — Freeze Errata & Clarification Record

**Date:** 2026-11-14  
**Status:** DOCUMENTARY ERRATA / INTEROPERABILITY CLARIFICATION — **NO LANGUAGE VERSION CHANGE**  
**Normative source:** [中文完整规范](../../../skill-language-spec.zh-CN.md)\
**Frozen target:** CA-SL vNext / API v1alpha3; §45.2 product conformance remains **NOT QUALIFIED**.

This errata follows the independent review after v1alpha3 was merged as PR #24. A [second post-freeze errata review](ca-sl-v1alpha3-errata-2026-11-14-r2.md) closes the later diagnostic, trust-input and terminology findings while preserving the frozen language version. It corrects cross-references and explains how existing refusal/authority rules apply to the teaching model. **It does not grant new provenance, enable an unknown Owner outcome, relax Reconcile authorization, or change the final status algorithm.** Any actual change to permitted identity sources, Owner proof semantics, or Reconcile output visibility would require a separately reviewed v1alpha4 (or later) contract, not silent v1alpha3 edits.

## Classification and resolution of the ten findings

| Review item | Classification | Resolution |
|---|---|---|
| §13.3 vs §28/§30 5GC request fields | Clarification, no new identity authorization | Request PSI/DNN/S-NSSAI may be ordinary selection fields in the **teaching Owner contract only**. If actual Owner/Scope marks a field as subject, session, lifecycle, correlation or resource identity, direct `context.request.*` is **invalid**; replace it with Host-verified or authoritative Producer value. E101 continues to reject untrusted request identity. |
| H incorrect/missing E links, E115/E116 | Errata | 23 overly broad or unsupported H mappings corrected to exact E cases or `待补独立 Fixture`. Removed undefined E115/E116; Code+Phase is now the unique diagnostic classification key (99 unique entries). Missing exact fixtures remain product qualification debt. |
| Reconcile Output Schema ambiguity | Terminology | §6.5 and §12.7 explicitly say Stage `reconcile-node.operation.output` is only the verified recovered subobject on COMMITTED, never the complete Owner query envelope or receipt. G.2 remains authoritative. |
| IndependentDomains not decodable | Trusted logical model clarification | G.3.1 spells out deploymentId, publisherId, snapshotDigest, canonical domain URI set and unique unordered nonreflexive pairs; F.4 requires independently authenticated deployment binding. No implicit authorization or transitive independence. |
| Runtime local gate table | Explanation | §12.9 table distinguishes Compiler path proof from Runtime current-Evidence/Scope/Scope-bound admission checks without adding a new implicit Predicate execution. |
| Route matrix in §22.1 only in Markdown | Informative tooling mirror | [Route matrix YAML](../fixtures/ca-sl-v1alpha3-route-matrix.yaml), explicitly subordinate to §22.1. Its conditional ownerOutcomes are not new permissions. |
| Normative E expectations vs actual fixtures | Informative traceability | [All E01–E114 indexed in YAML](../fixtures/ca-sl-v1alpha3-case-traceability.yaml); each has original input/expected text, known diagnostics, phase and termination hints, with `ciFixture: null` and no claim of implementation PASS. |
| Ambiguous E102 static vs Runtime | Clarification | E102 static sub-variants fail for missing/untrusted domain and fact mappings; independently valid schemas that cannot satisfy producer composition fail `PREDICATE_EVIDENCE_UNSATISFIABLE`; after successful linking, duplicate observed source records yield runtime Predicate UNKNOWN. |
| Duplicated §0 / §45 status | Intentional | §0 provides reader-facing status; §45 remains normative freeze/conformance gate. Repetition does not define two conflicting states. |
| Stage/Runtime diagnostic collision | Errata | H specifies `(Code, Phase)`; `EFFECT_MISMATCH` can occur at Compiler and Runtime, with distinct provenance, while OUTCOME_UNKNOWN is a Stage Outcome, never a diagnostic. |

## Critical requirement → code → test trace

| Clause | Expected Code / Outcome | E case | Actual executable CI evidence |
|---|---|---|---|
| §13.3, §28, §30 | `CALLABLE_ARGUMENT_PROVENANCE_INVALID` when request identity used without verified binding | E101 | Not established for v1alpha3 |
| §17.1.1, G.3/G.3.1, F.4 | `EVIDENCE_GUARANTEE_LINK_INVALID` / `PREDICATE_EVIDENCE_UNSATISFIABLE` (static), Predicate UNKNOWN (runtime) | E102 | Not established |
| §12.7, G.2/G.2.2 | `RECONCILE_CONTRACT_INVALID` / `CAPABILITY_NOT_GRANTED` | E107 | Not established |
| §20.3, G.2/G.2.2 | COMMITTED with recovered data, COMMITTED without data, NOT_COMMITTED, or COMMITTED_OUTPUT_UNAVAILABLE stop | E108 | Not established |
| §17.1, G.2 | Reconcile Producer outcome is Owner SUCCEEDED, not Runtime COMMITTED | E109 | Not established |
| §11.5, G.6 | `REQUEST_SCHEMA_MISSING` / `CONTEXT_REQUEST_COLLISION` | E113 | Not established |
| §22.1 | `ROUTE_OUTCOME_MISSING` and conditional declared Owner result routing | E55, E69, E76, E84 | Not established |

## Evidence and release boundary

Documentation hygiene is not a v1alpha3 Compiler test. The test metadata in the two YAML mirrors is not an assertion of passing Native, WASM, Studio, Runtime, Owner release, or real 5GC execution. The frozen language status remains unchanged; the **§45.2 gates are not satisfied** by creating these files.

A future code, integration or protocol change that would permit any unverified `context.request` identity field to stand in for Host/Owner provenance, or that would expose the entire Reconcile response as a Stage output, must use a new version rather than reinterpret this errata.

