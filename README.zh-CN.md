![ConnectionAgent Skills](assets/repo-banner.svg)

# ConnectionAgent Skills

ConnectionAgent 官方 Skill 源码仓。

这里维护供模型使用的 Skill 描述、Skill 自身的保障定义、资格验证用例、路由策略与模型上下文，以及编写 Skill 所需的文档和辅助工作流。

英文版：[`README.md`](README.md)

## 仓库结构

```text
ca-skills/
├── skills/                  # 官方 Skill 与路由策略源码
├── docs/                    # Skill 编写文档
├── scripts/verify.py        # 仓库统一验证入口
└── .agents/skills/
    └── create-connectionagent-skill/
```

可执行 Skill 通常采用下面的结构：

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/    # 可选
├── schemas/       # 可选
└── scripts/       # 可选，受治理的本地确定性计算
```

如果只是路由策略或模型上下文，可以只有 `SKILL.md`，再按需增加供模型读取的 `references/` 或 `schemas/`。

## 怎么写 Skill

先看：

- 中文：[`docs/authoring.zh-CN.md`](docs/authoring.zh-CN.md)
- 英文：[`docs/authoring.md`](docs/authoring.md)

仓库内用于辅助编写 Skill 的 Agent Skill 位于：

```text
.agents/skills/create-connectionagent-skill/
```

它的 `SKILL.md` 只保留编写流程和关键规则。具体的 YAML、脚本和用例语法放在 `references/authoring-syntax.md`，最终以 `ca-skill-toolchain` 当前的 Schema 和编译器为准。

几个常用约束：

- `SKILL.md` 是包根目录中供模型读取的入口；
- 可执行 Skill 使用完整的 `assurance/` 三件套；
- 当前没有独立的 `evidence.yaml`；
- 每个资格验证用例只使用一个 `cases/<case>/case.yaml`；
- Skill 根目录不使用 `README.md`、`MIGRATION.md`、`examples/`；
- `skills/` 下供模型读取的 Markdown 统一使用英文；
- 部署地址、ProviderBinding、ObservationBinding 和 Runtime 状态不写进 Skill 源码。

## 源码与执行

`skills/` 是官方 Skill 源码目录。

Skill Toolchain 从这里发现源码，完成编译并形成不可变的 `SkillBuildArtifact` / `ProcedureVariant` 后，Runtime 才会执行。Runtime 不直接执行当前工作区源码，因此仓库中的一次源码修改不会改变已经准入的构建产物，也不会影响历史运行记录。

用户从 ZIP、本地目录或 Git 导入的自定义 Skill 属于 Toolchain 的工作区与导入流程。导入成功不会把它自动写入本仓 `skills/`，也不会因此变成官方 Skill。

各仓职责可以简单看成：

| 仓库 | 主要职责 |
| --- | --- |
| `ca-skills` | 官方 Skill 源码与编写文档 |
| `ca-skill-toolchain` | Schema、编译、构建与资格验证 |
| `ca-agent` | 目标理解、路由与规划 |
| `ca-runtime` | 准入、绑定与确定性执行 |
| `ca-sandbox` | 受控环境与故障注入 |
| `ca-benchmarks` | 正式独立评测资产 |
| `ca-benchmark-engine` | 评测执行、裁决与认证 |

## 路由策略

`skills/5gc-intent` 是供 Agent 使用的路由策略与模型上下文包。它没有 `assurance/`，也不会先作为一个 Runtime Procedure 执行。

Agent 从 Runtime 已发现并准入的 Skill 集中做路由选择；最终执行前仍由 Runtime 对 `SkillBuildArtifact` / `ProcedureVariant` 做准入和绑定。

## 当前包

| 包 | 用途 | 当前状态 |
| --- | --- | --- |
| `5gc-intent` | 路由策略与模型上下文 | 非执行型 |
| `5gc-file-transfer` | 产品 Skill | 本地源码、编译、用例和 Q4 预检已通过；生产部署准入待完成 |
| `wifi-file-transfer` | 产品 Skill | 本地源码、编译、用例和 Q4 预检已通过；生产部署准入待完成 |
| `ue-registration` | 参考 Skill | 已通过生产级资格验证 |
| `ensure-session-qos` | 参考 Skill | 已通过生产级资格验证 |
| `download-object-by-deadline` | 参考 Skill | 已通过生产级资格验证 |
| `query-weather-for-ue` | 参考 Skill | 已通过生产级资格验证 |

两个文件传输 Skill 当前剩余的主要工作是生产部署和绑定关系收口，不是继续扩展 Skill 语法。

## 编写模型冻结

当前 Skill 语言和保障编写模型已经冻结。新增 Skill 和日常维护默认使用现有语言，不再因为便利性、部署差异、评测需求或局部实现问题扩展语法。

只有在真实产品场景证明现有语言存在表达能力缺口，并且该问题不能通过 ProviderBinding、ObservationBinding、Runtime、资格验证、Sandbox 或集成方式解决时，才允许启动语言变更。语言变更需要同步修改 Skill Toolchain 的 Schema 与编译器，以及受影响的官方 Skill、用例和编写文档，并重新通过 `make verify`，之后才能建立新的冻结基线。

## 验证

运行完整仓库验证：

```bash
make verify
```

只编译一个可执行 Skill：

```bash
python3 -B scripts/verify.py --compile skills/<name>
```

默认 Toolchain 兄弟目录为 `../ca-skill-toolchain`。如果目录不同，设置：

```bash
export CA_SKILL_TOOLCHAIN_ROOT=/path/to/ca-skill-toolchain
```

迁移期仍兼容 `CONNECTIONAGENT_SKILL_PLATFORM_ROOT`。

编译通过或本地预检通过，并不等于已经通过生产环境资格验证。
