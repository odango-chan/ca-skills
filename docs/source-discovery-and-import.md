# Official Skill Source Discovery

**状态：Repository Boundary Note**  
**更新时间：2026-09-09**

`connectionagent-skills` 是 ConnectionAgent Official Skill Source 的源码权威仓。

本文只说明本仓与 Source Discovery / Custom Import 的边界；完整跨仓模型以顶层 `connectionagent` 当前 machine contract / repository boundary 文档为准。

## 1. Official Skill 不需要手工 Import

正式 Skill 位于：

```text
skills/
└── <skill-package>/
```

ConnectionAgent deployment 应通过已配置的 `OfficialSkillSource` 自动发现这些 package，并交给 Skill Platform 建立 source snapshot、Catalog entry、Artifact/Variant。

正常产品路径不是：

```text
user opens Console
  -> manually import every official Skill
```

而是：

```text
OfficialSkillSource
  -> discovery
  -> Skill Platform
  -> Skill Catalog
  -> build / qualification
```

## 2. 固定逻辑 Source，不固定绝对路径

本仓定义源码资产；部署可以将同一版本映射到：

```text
checkout path
container image path
Desktop resource bundle
CI workspace
```

因此消费者应依赖 Source identity/version/digest 与 deployment configuration，不应在 Agent、Runtime 或 Web 中硬编码仓库 checkout 的绝对路径。

## 3. Custom Import 不写入本仓

用户通过 Web/Desktop/CLI 导入：

```text
ZIP
local directory
Git source
```

时，导入结果属于 Custom Source / Workspace。

它不能：

```text
copy into connectionagent-skills/skills and pretend to be Official
silently overwrite an Official Skill
obtain execution authority merely because import succeeded
```

只有经过明确治理后，一个 Custom Skill 才可能作为独立变更进入本仓。

## 4. Runtime 不直接读取本仓执行

当前正确链路：

```text
connectionagent-skills
  -> Skill Platform source snapshot
  -> immutable SkillBuildArtifact / ProcedureVariant
  -> qualification projection
  -> RuntimeHost discovery/context surface
  -> Agent selects an admitted Skill / Variant
  -> Agent loads selected Skill context and plans entrypoint/input
  -> RuntimeHost ProcedureExecutionRequest
  -> Runtime admission / ProviderBinding / deterministic execution
```

Runtime 执行请求以 immutable Artifact/Variant identity、entrypoint、input/context/correlation 为核心。

当前不重新引入：

```text
ExecutionTarget.v1
RunPlanSnapshot.v1
RunPlanRevision.v1
generic PlanDelta.v1
```

Runtime 不应在每次 Run 时扫描本仓 working tree 或直接执行 `SKILL.md`。Source 后续变化不能改变已经冻结的 Artifact/Variant identity 或历史 Run provenance。

## 5. Routing policy 资产

`skills/5gc-intent` 是 Agent-owned generic 5GC routing 的模型可见 policy asset。它没有 `assurance/`，也不是 Runtime 需要执行的前置 Procedure。

Agent routing 产生 `agent.routing_result@1` 语义事实，再从 Runtime 已发现/准入的 Skill 集中选择真实执行对象。Routing policy source 与 executable Artifact source 可以同仓维护，但执行权限边界必须保持分离。

## 6. 本仓成功标准

- `skills/` 保持 Official Skill Source / model policy asset 的清晰单一职责；
- Official executable Skill 可以被 deployment 自动发现、构建和资格验证；
- routing policy 不被误当成 Runtime execution hop；
- 仓库源码与 immutable execution Artifact 明确分层；
- Custom Import 不污染 Official Source；
- 每个构建结果能够追溯到明确 source revision/digest。
