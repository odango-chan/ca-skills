---
name: review-connectionagent-skill
description: Use when auditing, reviewing, migrating or refactoring any official ConnectionAgent Skill or its Procedure. Enforce the repository-wide Skill architecture review standard, 3GPP business-action granularity, Operation/Observation co-location, Host/Runtime/Owner boundaries, evidence and qualification rules.
---

# Review an official ConnectionAgent Skill

## Required reading

Before reviewing, read these sources from the target branch/commit:

1. AGENTS.md.
2. docs/skill-architecture-review.md — repository-wide mandatory review baseline.
3. docs/skill-language-spec.v1alpha4.zh-CN.md — frozen normative CA-SL language. Never change its semantics as part of a Skill review.
4. docs/current-5gc-skill-baseline.md and examples/MIGRATION-REVIEW-v1alpha4.md when reviewing the current 5GC examples.
5. docs/authoring-5gc-3gpp-profile.md for any 5GC Skill.
6. The Skill's complete SKILL.md, assurance/contract.yaml, assurance/procedure.yaml, assurance/predicates.yaml, Scripts, Schemas, references and Cases.
7. The exact Owner ToolCatalog, CapabilityContracts, Schema and Evidence publications when available. Proposals and urn:example values are not trusted publications.

## Review workflow

1. Pin the exact repository, branch, commit and Skill source path. Do not review a stale local copy or infer that an earlier CI result applies to the current head.
2. Establish the Skill goal, admitted request profile, excluded profiles and final business success criteria.
3. Build a Node inventory. For each Node identify its one primary business action, participating actors/NFs, source clause/step (for 5GC), classification and exact Operation callable.
4. Inspect Node stages in order: Precondition, primary Operation, optional Observation, Postcondition. The Operation is the primary action. Observation is normally a supplementary READ stage in the same Node, after the Operation and before Postcondition. They remain distinct stages/callable kinds but use the common Host Tool Dispatcher and trusted binding/authorization path. Do not create an Observation-only Node just to query facts for an adjacent action.
5. Check entry-time reads: when an Observation is required before any mutation, attach it to the earliest suitable read-only business Operation Node. Verify that it still runs before every session-creating or session-mutating Operation. Do not move a Skill business decision into Host admission.
6. Check post-Operation reads: attach a fresh Observation to the Node whose Operation it supports. Ensure it is not stale, not callback polling and not redundant with the Operation Result/Evidence.
7. Trace every argument to request input, subject context, a preceding Operation Result or an Observation Result. Check Schema assignability and exact Owner exports.
8. Audit each Predicate and Script for purity, determinism, declared inputs and absence of implicit global Context or network side effects.
9. Audit Host, Runtime and Owner responsibilities, especially business-instance identity, invocation lifecycle, async callbacks, duplicate/late messages, transport response obligations and reconciliation.
10. Audit READ/MUTATION effects, idempotency, competing operations, OUTCOME_UNKNOWN, safe stop, cleanup and resource responsibility.
11. Verify evidence authority, exact subject/resource/Invocation scope, occurrence binding, freshness and the distinction among absence, presence, unavailable projection and unknown.
12. Verify final Goal proof and all terminal branches. A transport acknowledgement or intermediate Operation success is not final business success unless the trusted contract says it is.
13. Compare the current source with the previous approved business behavior and Cases. Record omissions, intentional profile restrictions and unproven equivalence; do not silently drop business requirements.
14. Run only the repository checks available and report their exact commit, command, result and limitations. Do not claim Compiler, Link, Runtime, Qualification or live 5GC success from source hygiene.

## Mandatory 5GC checks

For 5GC Skills, additionally enforce:

- SMF point of view; one Node per logical 3GPP interaction or tightly related Request/Response group, not one Node per helper or every numbered substep.
- Exact TS/Release/clause/step and canonical service/procedure names.
- AMF, (R)AN and UE work remains assigned to those actors; the SMF-side inbound request/result is the relevant SMF boundary.
- Step 3/5 and Step 15/17 service ingress/exit responsibilities are explicitly assigned.
- Async UpdateSMContext completion resumes the exact pending Operation in the same Invocation; no new Skill, Wait, Await or polling Node.
- Non-SMF context is acquired inside the responsible Owner Tool. Direct Skill Observations are limited to required SMF-owned facts.
- Traditional 5GC Skills do not expose OpenAMSM internal module names or MAS implementation structure.

## Required report

Return a review with:

1. Exact reviewed commit and source paths.
2. Business/3GPP traceability and supported profile.
3. Node inventory: primary action, Operation, optional Observation, Postcondition and classification.
4. Findings grouped by P0, P1 and P2, with file/line evidence and concrete correction.
5. Tool/Capability/Schema/Evidence publication matrix.
6. Async, concurrency, mutation and terminal-path analysis.
7. Exact validation results and unverified/NOT_PUBLISHED/NOT_QUALIFIED gates.
8. A clear recommendation: APPROVE, REQUEST CHANGES or NOT_READY, without overstating evidence.

Do not modify the frozen CA-SL specification to accommodate an example. Do not invent Owner contracts. Do not merge a Skill source change until P0/P1 findings and the required cross-repository contracts are resolved or explicitly accepted.
