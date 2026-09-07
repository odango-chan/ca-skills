# Official Skill Source Discovery

**状态：Repository Boundary Note**  
**更新时间：2026-09-07**

`connectionagent-skills` 是 ConnectionAgent Official Skill Source 的源码权威仓。

本文只说明本仓与 Source Discovery / Custom Import 的边界；完整跨仓模型见顶层 `connectionagent/docs/skill-source-catalog-and-import.md`。

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

正确链路：

```text
connectionagent-skills
  -> Skill Platform source snapshot
  -> SkillBuildArtifact / CompiledProcedureVariant
  -> Agent Resolution
  -> Runtime admission / RunPlan
```

Runtime 不应在每次 Run 时扫描本仓的 working tree 或 `SKILL.md`。

这样 Source 的后续变化不会改变已经冻结的 Artifact、Variant 或历史 Run provenance。

## 5. 本仓成功标准

- `skills/` 保持 Official Skill Source 的清晰单一职责；
- Official Skill 可以被 deployment 自动发现；
- 仓库源码与执行 Artifact 明确分层；
- Custom Import 不污染 Official Source；
- 每个构建结果能够追溯到明确 source revision/digest。
