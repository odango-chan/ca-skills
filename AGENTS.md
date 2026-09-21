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


## WORK.md v2 — 当前状态文档硬规则

`docs/WORK.md` 只描述当前事实，不承担工程日志、历史时间线或完整验收报告。WORK 只回答：当前职责、总体状态、已完成、未完成、blocker、下一步。

统一状态：
```text
Design:          PROPOSED | ACCEPTED
Implementation:  NOT_STARTED | PARTIAL | IMPLEMENTED
Acceptance:      NOT_RUN | BLOCKED | FAIL | PASS
Roll-up:         VERIFIED | DEFERRED | RETIRED
```
`ACCEPTED != IMPLEMENTED`；`IMPLEMENTED != PASS`；只有 REQUIRED acceptance 全部 PASS 才能写 `VERIFIED`。

禁止在 WORK 末尾追加按日期排列的实施日志、完整测试输出、临时目录/端口、旧 correction、raw evidence、architecture/design/ADR 正文。历史过程由 Git/PR/Issue 保留，raw evidence 放 `artifacts/acceptance/<run-id>/`，active migration detail 放 `docs/migration/` 或 `docs/work/<workstream>/`。

WORK 目标约 200～300 行；超过 400 行必须先治理再追加。状态变化时原位改写旧结论；关闭项从 Open work 删除；跨仓 owner live status 只引用，不手抄第二份。

### WORK 刷新模板（必须原位刷新，不追加日志）

```markdown
# <repo> 当前工作状态

Updated: YYYY-MM-DD

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
