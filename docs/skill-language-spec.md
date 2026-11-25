# CA-SL v1alpha5 — Current specification / 当前语言规范入口

**Language identifier / 语言标识：** connectionagent.io/v1alpha5.

## Published baseline

Until the same-version refresh proposal below is merged, the current published normative baseline remains the 2026-11-17 release:

- [CA-SL v1alpha5 published normative source](https://github.com/odango-chan/ca-skills/blob/0abfd0e1ab99f481a4ae01f3f47efc54783dd5e5/docs/skill-language-spec.v1alpha5.zh-CN.md)
- [Published v1alpha5 release record](releases/ca-sl-v1alpha5.md)

## Proposed v1alpha5 refresh

- [Candidate complete specification](skill-language-spec.v1alpha5.zh-CN.md)
- Candidate branch: refresh-ca-sl-v1alpha5-skill-selection-when
- The proposal keeps the v1alpha5 language identifier and adds optional Assurance, top-level assurance/contract.yaml.when, Skill selection semantics and source/Artifact import rules.
- On review and merge, the candidate becomes the current v1alpha5 normative source and supersedes the 2026-11-17 text under the same language identifier. No v1alpha6 or old-format compatibility is introduced.

## Companion contracts

- **IngressCatalog:** connectionagent.io/ingresscatalog/v1alpha1 — FROZEN / RELEASED (logical contract only).
- **Ingress diagnostics:** connectionagent.io/ingress-diagnostics/v1alpha1 — FROZEN / RELEASED.
- **Inherited external profiles:** connectionagent.io/toolcatalog/v1alpha4 and connectionagent.io/capability-contracts/v1alpha4 retain their own exact version identities; this refresh does not rewrite them.

## Qualification boundary

Compiler / Studio / Host / Runtime / Skill Importer / Owner / Integration / 5GC remain NOT_QUALIFIED until separately tested and backed by trusted publication/deployment evidence under §45.2, §L.13.2 and the applicable Appendix M cases.

CA-SL v1alpha4 remains an immutable historical language target for explicitly selected v1alpha4 builds. It is not silently reinterpreted as v1alpha5.
