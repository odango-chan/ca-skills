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


## 1. Overall
一句话说明当前阶段与最主要剩余工作。

## 2. Current scope matrix
| Scope | Implementation | Acceptance | Remaining |
| --- | --- | --- | --- |
| <scope> | NOT_STARTED / PARTIAL / IMPLEMENTED | NOT_RUN / BLOCKED / FAIL / PASS | <一句话；完成则写 —> |

## 3. Open work
### P0
- <当前必须先完成的 1～5 项>
### P1
- <后续项；没有则省略>

## 4. Blockers
- <blocker -> owner/dependency -> 解除条件>
- 无 blocker 时写 `None.`

## 5. Next actions
1. <下一步>
2. <下一步>
3. <下一步>

## 6. Authority / evidence links
- Design: <canonical path>
- Acceptance: <matrix/ledger path>
- Latest evidence: <artifact locator>
- Cross-repo owner: <owner WORK/path，若适用>
```

刷新规则：实现变化改 matrix；case 执行只更新 Acceptance 和 evidence locator；blocker 原位增删；阶段关闭删除 open item；下一步直接重排；设计变化先改 canonical；跨仓依赖只引用 owner 当前状态。
除非新增全新当前 scope，否则 WORK 更新默认应让文件长度持平或缩短。


### 现有 WORK.md 迁移流程（先迁移，再压缩）

对已经膨胀的 `docs/WORK.md` 做治理时，**禁止直接摘要后覆盖原文件**。必须按以下顺序执行：

```text
1. Inventory
   - 读取改动前完整 WORK
   - 标出每一段当前唯一承载的信息

2. Classify
   - 当前状态 / open work / blocker / next action -> 留在 WORK
   - 稳定语义 / 长期约束 -> architecture/design
   - 决策原因 -> ADR
   - 仍在进行的迁移细节 -> migration/workstream
   - acceptance case 当前结果 -> acceptance ledger/matrix
   - raw evidence / run detail -> artifacts/acceptance
   - 已结束的纯过程流水 -> Git/PR/Issue history

3. Migrate before delete
   - 某段若仍是唯一的人类可读 authority/index，先迁移到正确 canonical 文档
   - 确认目标文档存在且引用可追踪后，才允许从 WORK 删除
   - 不得用“Git 里还能找”替代尚未迁移的当前 authority

4. Verify
   - 检查 caseId / evidence locator / canonical links 没有丢失
   - 检查没有把历史 PASS 冒充 current PASS
   - 检查跨仓 owner 状态改为引用而不是复制

5. Compact
   - 最后才按 WORK v2 六区块模板重写 snapshot
   - compact 后 WORK 只保存 current truth
```

迁移时必须保留的信息类型：
- 仍被 acceptance matrix 引用的 case/result/evidence locator；
- 尚未进入其他 canonical 文档的稳定约束或边界；
- 当前 migration/cutover 的执行条件、删除 gate、兼容条件；
- 当前 blocker 的解除条件；
- 仍需后续复验的历史 evidence 基线。

可以直接依赖 Git history 而不另建 archive 的内容：
- 已关闭且已被当前结论完全取代的逐日修复流水；
- 临时端口、PID、scratch 目录等一次性执行细节；
- 已有 immutable artifact 保存的完整 stdout/stderr；
- 已被 canonical ADR/design 吸收的讨论过程。

**判断不清时默认先迁移/保留，不默认删除。**

## Documentation & WORK Governance

- 跨仓文档规则以 `odango-chan/connectionagent/docs/DOCUMENTATION.md` 为唯一治理基线；本仓只补充 owner-local 例外。
- `README` 只做定位/Quick Start/导航；一个主题只保留一个 canonical source；machine schema/public types/executable behavior/immutable evidence 高于 prose。
- `docs/WORK.md` 只保存**当前快照**，固定为：`Overall`、`Current scope matrix`、`Open work`、`Blockers`、`Next actions`、`Authority / evidence links`。没有 live work 时不为模板强建空 WORK。
- WORK 状态只用：Design=`PROPOSED|ACCEPTED`；Implementation=`NOT_STARTED|PARTIAL|IMPLEMENTED`；Acceptance=`NOT_RUN|BLOCKED|FAIL|PASS`；Roll-up=`VERIFIED|DEFERRED|RETIRED`。`IMPLEMENTED != PASS`。
- 状态变化必须**原位刷新**表格/条目：case 完成只更新结果与 evidence locator；blocker 解除就删除；阶段关闭从 Open work 移除；禁止追加日期流水、`implementation update`、`correction`。
- WORK 目标约 200～300 行；超过 400 行先治理，不能继续堆历史。
- 治理已有膨胀 WORK 必须按 `Inventory -> Classify -> Migrate before delete -> Verify -> Compact` 执行；若某段仍是唯一的人类可读 authority/index，先迁移并验证引用，再删除。
- 归位：稳定语义→architecture/design；why→ADR；活动迁移→migration/workstream；case 当前结果→acceptance matrix/ledger；raw run→`artifacts/acceptance/`；纯历史→Git/PR/Issue。
- 顶层/集成仓不得复制 owner live status；只引用 owner WORK 或 mechanically generated status。判断不清时默认先迁移/保留，不默认删除。
