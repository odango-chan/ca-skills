# CA-SL v1alpha5 Release Record

**Status:** REFRESH PROPOSAL — not yet released
**Current published release date:** 2026-11-17
**Proposed refresh date:** 2026-11-25
**Language target:** connectionagent.io/v1alpha5

## 1. Current published normative baseline

Until the refresh proposal is reviewed and merged, the current published v1alpha5 baseline remains:

- **Complete normative source:** [docs/skill-language-spec.v1alpha5.zh-CN.md at the published baseline](https://github.com/odango-chan/ca-skills/blob/0abfd0e1ab99f481a4ae01f3f47efc54783dd5e5/docs/skill-language-spec.v1alpha5.zh-CN.md)
- **Published normative commit:** 0abfd0e1ab99f481a4ae01f3f47efc54783dd5e5
- **Publication PR:** [ca-skills #66](https://github.com/odango-chan/ca-skills/pull/66)
- **Merge commit:** 0abfd0e1ab99f481a4ae01f3f47efc54783dd5

This commit remains historical and reproducible. The refresh proposal does not silently rewrite the already published baseline.

## 2. Proposed same-version refresh

- **Proposal branch:** refresh-ca-sl-v1alpha5-skill-selection-when
- **Candidate normative source:** [docs/skill-language-spec.v1alpha5.zh-CN.md at candidate commit](https://github.com/odango-chan/ca-skills/blob/baaec88d2949213d7fe5d7ed436d4bd892cc2f24/docs/skill-language-spec.v1alpha5.zh-CN.md)
- **Candidate commit:** be0ba11270037eda76137f535ec4ba65bcb0da8f
- **Language identifier:** remains connectionagent.io/v1alpha5; no v1alpha6 is introduced.
- **Publication status:** pending review and merge. On approval, this candidate supersedes the 2026-11-17 normative text under the same language identifier.

### Normative changes proposed

1. Every Skill package has SKILL.md; assurance/ is optional.
2. contract.yaml remains inside assurance/ and is not required for SKILL.md-only Skills.
3. Valid Assurance enables both Deterministic and LLM-guided modes; no Assurance means LLM-guided only; invalid present Assurance fails import and cannot silently downgrade.
4. Add optional top-level assurance/contract.yaml.when as a pure CEL Skill-selection expression over event.type and typed input.
5. Keep contract.when separate from execution-time predicates.yaml.
6. Define formal true-match selection, semantic selection of unguarded SKILL.md candidates, and fail-closed behavior.
7. Define SKILL.md-only import, Assurance source compilation, and compiled Artifact Inspect/Verify/Admission without rebuild.
8. Distinguish LLM Action proposals (Runtime Action Boundary; no Compiler) from LLM-created/edited Assurance source (normal Compiler import path).
9. Add SA-001–SA-011 normative selection/import expectations.

The refresh does not add a Domain Contract Package, TaskContract Package, supportedModes, a second LLM Contract, package signatures, Trust Registry or legacy compatibility.

## 3. Companion Ingress contract

- **IngressCatalog:** connectionagent.io/ingresscatalog/v1alpha1
- **Diagnostic registry:** connectionagent.io/ingress-diagnostics/v1alpha1
- **Companion contract:** [integration-ingress-operation-contract-vnext.zh-CN.md](https://github.com/odango-chan/ca-skills/blob/9412be9894ef36acf846c757a5870dc0c48b33ac/docs/design/integration-ingress-operation-contract-vnext.zh-CN.md)
- **Diagnostic registry:** docs/design/ingress-diagnostic-registry-v1alpha1.md and docs/design/ingress-diagnostic-registry-v1alpha1.json
- **Companion release commit:** 9412be9894ef36acf846c757a5870dc0c48b33ac
- **Publication PR:** [ca-skills #62](https://github.com/odango-chan/ca-skills/pull/62)

The refresh does not change the IngressCatalog or its diagnostic registry.

## 4. Validation status

- The 2026-11-17 release verification remains evidence for the original published baseline only.
- The refreshed normative document has not yet passed the repository's documentation/source-hygiene checks in this proposal branch.
- Compiler, Studio/LSP, Host, Runtime, Skill Importer, Integration Adapter, Owner and live 5GC qualification are not established by this documentation change.
- The Compiler must explicitly support the refreshed contract.when field and the Assurance-free Skill import boundary before those behaviors can be claimed as implemented.

Do not treat normative text, a passing documentation validator or a merged specification as proof of product conformance.

## 5. Compatibility and qualification

- CA-SL v1alpha4 remains an immutable historical language target.
- The current published v1alpha5 baseline remains the 2026-11-17 release until this proposal is merged.
- The proposed refresh keeps the v1alpha5 language identifier and supersedes the previous v1alpha5 text only after review/merge.
- No old-format compatibility mapping is introduced.
- Compiler, Studio/LSP, Host, Runtime, Importer, Owner publication, deployment binding and 5GC E2E remain NOT_QUALIFIED until separately verified with real implementation and deployment evidence.
