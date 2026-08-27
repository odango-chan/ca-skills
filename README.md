# ConnectionAgent Skills

`connectionagent-skills` 是 ConnectionAgent **正式 Skill 资产仓**。

本仓负责维护可被 Skill Platform 编译、校验和消费的 Vendor Skill 包；不实现 Skill Platform、Agent、Runtime、Sandbox 或 Web 的运行逻辑。

## 边界

本仓拥有：

- `SKILL.md`；
- Skill-local `assurance/`；
- Vendor `cases/`；
- `references/`；
- Skill-local `scripts/` 与其元信息；
- Skill 示例与说明。

本仓不拥有：

- Skill Compiler / ProcedurePatch Apply / SkillProfile Resolver：`connectionagent-skill-platform`；
- LLM / Agent loop / model adapter：`connectionagent-agent`；
- Procedure execution / Session / Event / Evidence / Reconcile：`connectionagent-runtime`；
- 5GC simulated world / fault injection：`connectionagent-sandbox`；
- 正式 UI：`connectionagent-web`。

## 目录

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── assurance/
    ├── cases/
    ├── references/
    ├── scripts/
    └── examples/
```

## 迁移原则

正式 Skill 从 `connectionagent-skill-platform/skills/` 逐步迁入本仓。迁移采用 additive-first：

1. 先在本仓建立等价资产并校验；
2. Skill Platform 改为从独立 Skill 资产输入进行集成验证；
3. 最后从 Skill Platform 删除正式 Skill，只保留 compiler/schema 所需最小 fixture。

第一批迁移：`ue-registration`。
