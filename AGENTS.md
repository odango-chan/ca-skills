# AGENTS.md

## Repository role

`ca-skills` contains official ConnectionAgent Skill source and model-visible routing-policy assets.

Keep Platform, Runtime, Sandbox, Benchmark, Agent-loop, and UI implementation out of this repository.

## Working rules

- Official packages live under `skills/<package>/`.
- `SKILL.md` is the package-root **model-facing** entry point. Keep it thin and focused on domain semantics, normalization, selection/use conditions, and boundaries the model must not guess or bypass.
- Model-facing Markdown under `skills/` is written in English.
- An executable Skill uses the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio. Do not add a standalone `evidence.yaml`.
- Qualification cases use one `cases/<case>/case.yaml` per case. Case coverage follows semantic obligations; do not hard-code a required case count in repository scripts.
- Package-root `README.md`, `MIGRATION.md`, and `examples/` are not part of the official package shape.
- `references/preload/` is only for small domain context needed on most invocations. Put optional Skill-local detail under `references/on-demand/`; neither directory should become an architecture manual.
- Skill-local `scripts/` are governed deterministic local-compute assets. Do not hide Provider I/O, network access, credentials, or deployment logic in them.
- Do not place ProviderBinding, ObservationBinding, deployment endpoints, Runtime state machines, Sandbox worlds, Benchmark scoring, or Web behavior in Skill model context.

## Authoring guidance

Human guides:

- English: `docs/authoring.md`
- Chinese: `docs/authoring.zh-CN.md`

Repository-local authoring workflow:

```text
.agents/skills/create-connectionagent-skill/
```

Its `SKILL.md` contains workflow and loading rules. Load `references/authoring-syntax.md` only when editing assurance source, governed Scripts, or Cases. Use `references/skill-granularity.md` when deciding Skill vs routing policy vs Runtime Capability.

Do not duplicate the full Skill grammar in `AGENTS.md`, README, or other prose. The current machine schemas/compiler in `ca-skill-toolchain` are authoritative.

For current official `assurance/procedure.yaml`, author against `schemas/v1alpha1/procedure-source.schema.yaml`, not historical/internal procedure source shapes.

## Source and execution boundary

- `skills/` is the official source catalog.
- Skill Platform freezes/compiles source before Runtime execution; Runtime does not execute the live working tree.
- Custom ZIP/directory/Git imports belong to the Platform workspace/import flow and must not write into `skills/` or silently become official source.
- Routing is Agent-owned. A routing-policy package such as `5gc-intent` is model context, not a preliminary executable Runtime hop.

## Verification

Use the single repository verification entrypoint:

```bash
make verify
```

For one executable package:

```bash
python3 -B scripts/verify.py --compile skills/<name>
```

Do not add per-Skill root validators or another compile helper. Generic source-language validation belongs to Skill Platform; package hygiene belongs in `scripts/verify.py`.

Compile or local preflight success is not production qualification.

## Ownership

- Skill source and authoring guidance: `ca-skills`
- Machine schemas, compiler, Artifact/Variant build, Qualification: `ca-skill-toolchain`
- Goal interpretation, routing, planning/model loop: `ca-agent`
- Admission, Provider/Observation binding, Evidence Gate, deterministic execution, Reconcile: `ca-runtime`
- Environment simulation, fault injection, ground truth: `ca-sandbox`
- Independent evaluation cases and verdicts: `ca-benchmarks`
- Product UI: `ca-console`

## Frozen authoring model

The current Skill language and assurance authoring model are frozen.

Do not change source syntax for convenience, cleanup, provider differences, deployment binding, qualification shortcuts, or benchmark-specific needs.

A language change is allowed only when a concrete product scenario demonstrates an expressiveness gap that cannot be solved by ProviderBinding, ObservationBinding, Runtime behavior, qualification, Sandbox, or integration work.

When such a gap is proven, treat the change as a language revision. Update the owning Skill Platform schemas/compiler together with official Skill examples and Cases, authoring guidance, and compatibility notes as needed. Re-run `make verify` before establishing a new frozen baseline.
## Cross-repository Documentation Governance

跨仓统一文档治理以 `odango-chan/connectionagent/docs/documentation.md` 的 **跨仓统一文档治理 Profile** 为基线。本仓可以补充更严格的本地规则，但不得建立冲突的第二套生命周期或 authority 模型。

执行文档任务时遵守：

- `README.md` 只做仓库定位、Quick Start 和导航，不复制第二套架构正文；
- `docs/README.md`（存在时）是文档地图和固定阅读顺序；
- `docs/DOCUMENTATION.md`（存在时）维护本仓 Canonical Source Map、目录职责和局部例外；
- `docs/WORK.md`（存在时）是当前实现/readiness/blocker/acceptance evidence 的唯一 live source，不承担长期设计 authority；
- 长期边界/ownership 放 `docs/architecture/`，本仓实现契约放 `docs/design/`，why 放 `docs/decisions/`，迁移/compatibility/acceptance 放 `docs/migration/`，示例放 `docs/examples/`；没有内容时不为模板创建空目录；
- canonical prose 的设计状态统一为 `Draft | Proposed | Accepted | Deprecated`；`Accepted` 只表示 human-readable development baseline，不等于代码已实现、machine contract ready、integration ready 或 VERIFIED；
- 新建文档前先搜索现有 canonical topic；已有正文则原地更新，不创建 `final/latest/v2/detailed-design/review` 等平行副本；
- machine schema/public types/executable behavior/canonical fixture/immutable result 高于 prose；发现冲突时修 canonical contract/prose，不以 consumer 文档或示例覆盖 owner authority；
- 一次性 review、prompt、短期 inventory 优先留在 PR/Issue/review/local scratch；需要跨多个 PR/Agent 的长期实施工作再进入 migration/workstream 机制；
- 现存目录、状态或重复文档问题属于治理债务；除非当前任务就是 documentation-governance cleanup，不顺手大规模搬迁/重命名旧文档；
- 文档变更后运行本仓已有的 docs/link/schema validation；没有自动检查时至少核对 canonical source、相对链接、状态元数据和引用闭合。未实际执行的 Gate 必须报告 `NOT RUN`，不得写成 PASS。

