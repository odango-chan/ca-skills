![ConnectionAgent Skills](assets/repo-banner.svg)

# ConnectionAgent Skills

ConnectionAgent 官方 Skill 源码与编写规范仓库。

## 当前 5GC 基线

当前 5GC 源码基线包含两个独立的可执行 Skill：

| 包 | 业务范围 |
| --- | --- |
| `establish-pdu-session` | 传统 5GC UE 请求的初始 PDU Session Establishment 流程 |
| `establish-pdu-session-mas` | 基于 SMF MAS policy-first 流程的 UE 请求初始 PDU Session Establishment |

两个包均同步自 `odango-chan/ca-agent-demo` main，源提交为 `4395982fa6efb97714b97901603b2dfb7018c4d0`。详见[源码与兼容性记录](docs/current-5gc-skill-baseline.md)。

仓库同时包含只读导入的 ToolCatalog 快照：`lib/tools/createdsession.tool.yaml`。它包含传统 Skill 使用的 12 个 Operation，但不包含 MAS Skill 引用的 16 个 Operation；MAS 的设计稿 Tool Contract 不作为已批准的导入契约。

**验证状态：** 本次完成的是源码同步，不代表编译、链接或 Runtime 资格验证通过。传统 Skill 的 Procedure 使用节点级 `preconditions/postconditions`，旧版 Toolchain Schema 尚不支持；MAS Skill 仍有 16 个未解析的 Operation 引用（同时用作资源授权）；其设计稿 ToolCatalog 不作为正式依赖导入。无状态 Compiler v0 设计已经确认，但新编译器尚未实现。

## 仓库结构

```text
ca-skills/
├── skills/                  # 官方 Skill 源码
├── lib/                     # 外部导入的只读契约
├── output/                  # 编译生成产物（不提交）
├── docs/                    # 编写指南与维护文档
├── spec/                    # 机器可读的语言 Token/引用目录
├── scripts/verify.py        # 现有旧版验证入口
└── .agents/skills/           # 仓库内编写助手
```

项目采用 `skills/` + `lib/` + `output/` 三根目录：`skills/` 是可编辑的 Skill 源码，`lib/` 是只读导入契约，`output/` 是只读生成产物。目录权限、图标和 Explorer 交互约定见[项目目录规范](docs/project-layout.md)。

## 编写入口

- 中文：[Skill 编写指南](docs/authoring.zh-CN.md)
- English: [Authoring guide](docs/authoring.md)
- [Skill Language Specification（中文）](docs/skill-language-spec.zh-CN.md)
- [Skill Language Specification (English)](docs/skill-language-spec.md)
- [语义 Token 目录（供 Studio/LSP 消费）](spec/skill-language-tokens.yaml)
- [Skill Language Specification（中文）](docs/skill-language-spec.zh-CN.md)
- [Skill Language Specification (English)](docs/skill-language-spec.md)
- [当前 Authoring Model](docs/authoring-model.md)
- [当前 5GC Skill 基线](docs/current-5gc-skill-baseline.md)

`SKILL.md` 面向模型，描述业务语义；`assurance/` 保存确定性流程源；`references/` 是可选的平铺 Markdown 知识；`scripts/` 只做受治理的本地确定性计算。

## 仓库职责

| 仓库 | 职责 |
| --- | --- |
| `ca-skills` | 官方 Skill 源码与领域编写语义 |
| `ca-skill-toolchain` | 旧版机器 Schema/Compiler 与现存 Toolchain |
| `ca-skill-compiler` | 目标无状态多 Skill Compiler；目前仅 bootstrap，尚未实现 |
| `ca-agent-demo` | Generic Agent Host 参考实现与当前源码样例 |
| `ca-runtime` | 准入、操作权威、Evidence 与确定性执行 |

仓库中其他旧包暂时原样保留，但不属于当前 5GC 基线，也不再作为当前语法示例。
