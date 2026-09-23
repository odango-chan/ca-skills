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

## Documentation & WORK Governance

- 跨仓文档治理以 `odango-chan/connectionagent/docs/DOCUMENTATION.md` 为基线；本仓只保留 Skill source / authoring 的 owner-local 规则。
- README/authoring 文档只做定位、使用和 authoring guidance；不要复制 machine schema/compiler grammar。
- 本仓没有 live implementation work 时不为了统一模板创建空 `docs/WORK.md`。
- 若未来出现持续实施工作，需要 WORK 时只保存 current snapshot，并按 `Inventory -> Classify -> Migrate before delete -> Verify -> Compact` 治理；历史流水留给 Git/PR/Issue。

## Issue / audit trail discipline

发现本仓或其他仓存在**可执行的问题/需求/缺口**（包括实现缺陷、产品/工程需求、feature/change request、文档漂移、缺失 contract/test/evidence、治理遗漏、cleanup/technical debt）时，不得只留在聊天、WORK 或提交说明里：

- 先在真正 owning repository 搜索现有 open Issue；已有等价 Issue 时复用并补充新证据，不重复创建。
- 没有等价 Issue 时，在 owner 仓创建 Issue；跨仓问题以 authority/code owner 仓为主 Issue，consumer 仓直接引用。只有 consumer 自身存在独立实施/验收工作时才额外建 local Issue。
- Issue 至少写清：Observed evidence/locator、Expected/target、影响范围/相关仓、owner、关闭条件/acceptance；blocker 还要写 blocking contract/file 与解除条件。
- 当前任务会修复时，Issue 应在修复前或最迟与第一笔修复提交同时建立；实施 commit message/body 必须引用 Issue（同仓可用 `#N`，跨仓用 `owner/repo#N`）。
- **提交代码不等于可以关 Issue。** 只有修复已进入目标分支，并完成该问题要求的 local/focused/acceptance Gate 后才能关闭。
- 关闭前在 Issue 留下 resolving commit(s)、实际执行的 test/acceptance result、stable evidence locator，以及仍未覆盖的 scope；若只完成部分条件，保持 Issue open。
- 若发现的问题不属于当前任务 scope，不要顺手扩大实现范围；创建/更新 Issue 后保留 open，交给后续 workstream。
- Issue 负责 actionable tracking / 历史审计；`WORK.md` 仍只保存 current snapshot，`TRACEABILITY.md` 仍负责 contract -> code -> test -> acceptance -> evidence。关闭 Issue 不能替代 WORK/TRACEABILITY 同步。
- `WORK.md` 不维护 `Open work` / `Next actions` prose backlog；actionable work、需求与 blocker 进入 owner Issue，WORK 只保留状态与 Issue ref。

## Agent scratch / temporary storage

本机 `/tmp` 可能是容量有限的 RAM-backed tmpfs。大下载、依赖缓存、解压目录、构建中间产物、浏览器/测试数据、artifact，以及需要跨多个命令保留的状态不得默认放在 `/tmp`。

```bash
AGENT_TMP="${CA_AGENT_TMPDIR:-$PWD/.agent-tmp}"
mkdir -p "$AGENT_TMP"
export TMPDIR="$AGENT_TMP"
export TMP="$AGENT_TMP"
export TEMP="$AGENT_TMP"
```

- 若设置 `CA_AGENT_TMPDIR`，优先使用该目录；它应位于容量充足、非 tmpfs 的磁盘；
- 未设置时使用仓库内 `.agent-tmp/`；
- `/tmp` 只用于小型、短生命周期、随时可丢弃的文件；
- 调试、恢复或跨命令需要的中间状态不要只存在 `/tmp`；
- 长时间或大 IO 任务开始前检查可用空间；
- 只清理由当前任务创建的 scratch；不得扫描、停止或删除其他任务、用户或 Agent 的进程、文件或临时目录。

