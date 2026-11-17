# CA-SL v1alpha5 Release Record

**Status:** FROZEN / RELEASED  
**Release date:** 2026-11-17  
**Language target:** `connectionagent.io/v1alpha5`

## Normative identity

- **Complete normative source:** `docs/skill-language-spec.v1alpha5.zh-CN.md`
- **Immutable normative commit:** `0abfd0e1ab99f481a4ae01f3f47efc54783dd5e5`
- **Publication PR:** [ca-skills #66](https://github.com/odango-chan/ca-skills/pull/66)
- **Merge commit:** `0abfd0e1ab99f481a4ae01f3f47efc54783dd5e5`

The normative source is the complete single file at the commit above, including the inherited v1alpha4 normative baseline, the v1alpha5 diagnostic index in Appendix H, and the Node-entry Event Wait amendment in Appendix L. This release record is stored separately because a specification file cannot embed its own commit SHA without changing that SHA.

## Companion Ingress contract

- **IngressCatalog:** `connectionagent.io/ingresscatalog/v1alpha1`
- **Diagnostic registry:** `connectionagent.io/ingress-diagnostics/v1alpha1`
- **Companion contract:** `docs/design/integration-ingress-operation-contract-vnext.zh-CN.md`
- **Diagnostic registry:** `docs/design/ingress-diagnostic-registry-v1alpha1.md` and `docs/design/ingress-diagnostic-registry-v1alpha1.json`
- **Immutable companion release commit:** `9412be9894ef36acf846c757a5870dc0c48b33ac`
- **Publication PR:** [ca-skills #62](https://github.com/odango-chan/ca-skills/pull/62)

Appendix H.1 composes the ten Ingress diagnostic identities into the CA-SL v1alpha5 Compiler diagnostic index while preserving the versioned Ingress registry as their owner.

## Release verification

- **CA-SL v1alpha5 Source Hygiene:** PASS — [GitHub Actions run 44104997656](https://github.com/odango-chan/ca-skills/actions/runs/44104997656)
- **Documentation structure:** PASS — includes the v1alpha4 inherited baseline, v1alpha5 release status, Appendix L and exact H/H.1 diagnostic counts.
- **Wait obligation register:** PASS — 36 normative obligations; product execution remains NOT_RUN.
- **Ingress diagnostic registry:** PASS — 10 exact identities; product execution remains NOT_RUN.
- **Documentation regression tests:** PASS — 7 tests.
- **IngressCatalog Schema / artifact lock:** PASS — [run 44103361389](https://github.com/odango-chan/ca-skills/actions/runs/44103361389)
- **Ingress Source Hygiene:** PASS — [run 44103361387](https://github.com/odango-chan/ca-skills/actions/runs/44103361387)

The repository checks validate source hygiene, normative document structure and registry integrity. They are not Compiler, Studio/LSP, Host, Runtime, Integration Adapter, Owner or live 5GC product-conformance tests.

## Compatibility and qualification

- CA-SL v1alpha4 remains an immutable historical language target.
- v1alpha5 is the current authoring target.
- The Compiler must select one exact language target; no fallback or silent reinterpretation is permitted.
- EW-001–EW-036 remain normative test obligations and are not claimed as executed product tests.
- Compiler, Studio/LSP, Host, Runtime, Integration Adapter, real Owner publication, deployment binding and 5GC E2E remain **NOT_QUALIFIED** until separately verified with real implementation and deployment evidence.

Language freeze and release do not imply product qualification.
