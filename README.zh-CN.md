![ConnectionAgent Skills](assets/repo-banner.svg)

# ConnectionAgent Skills

ConnectionAgent 官方 Skill 源码与语言契约仓库。

## 权威边界

**本仓库是官方 Skill 源码和语言语义的唯一输入权威。** `ca-agent-demo` 用于核对当前实际运行行为、刷新样例；Compiler 和 Studio 应消费本仓库的正式源码。

## v1alpha4 PDU Session 示例

两个使用 v1alpha4 作者语法的 Skill 位于 **[`examples/skills/`](examples/README.md)**：

| 示例 | 业务 | 验收状态 |
|---|---|---|
| `examples/skills/establish-pdu-session` | 传统 UE 请求初始会话 | 仅源码形状；Owner 链接 NOT_QUALIFIED |
| `examples/skills/establish-pdu-session-mas` | MAS policy-first | 仅源码形状；MAS Owner 未发布，不可声称编译/运行通过 |

原有完整 v1alpha1/v0.2 源码、全部 Case 和五个 Script 已保存在 `examples/legacy/`，只用于业务对照，**不可作为 v1alpha4 编译输入**。`lib/tools/createdsession.tool.yaml` 是旧版 12 Operation 历史快照，不能通过改 apiVersion 冒充真实 v1alpha4 发布物。

新的示例明确使用 `urn:example` 标记未发布的外部 Owner / Evidence 依赖。严格 Compiler 在缺少可信 v1alpha4 ToolCatalog、CapabilityContracts 和 Host/Schema 快照时必须拒绝链接，不能虚构通过。

## 语言与编写规范

- [当前 CA-SL v1alpha4 语言规范](docs/skill-language-spec.v1alpha4.zh-CN.md)
- [Script 契约 v0](docs/script-contract.md)
- [Schema 所有权](docs/schema-ownership.md)
- [Authoring Model](docs/authoring-model.md)
- [Skill 包目录规范](docs/project-layout.md)
- [当前 5GC 源码基线](docs/current-5gc-skill-baseline.md)
- [语义 Token 注册表](language/semantic-tokens.v1.json)
- English: [Authoring Guide](docs/authoring.md)
- 中文：[Skill 编写指南](docs/authoring.zh-CN.md)

## Compiler 边界

Compiler 接收调用方提供的源码和外部契约字节，解析/链接 Skill 语言，进行静态校验，生成 Script Output Schema，并返回确定性的文件集合。

Compiler **不**负责获取或管理依赖、不连接 Git/Upload/MCP、不维护 Lock/Cache、不运行 Python、不执行 Tool、不运行 Qualification，也不宣称 Runtime READY。Studio/调用方负责组装 `files` 和 targets，并决定如何展示/导出 BuildResult。

当前迁移状态：
- [ca-skill-compiler PR #3](https://github.com/odango-chan/ca-skill-compiler/pull/3)：v0 Closeout 已准备 Review；完整 v0 实现仍为 PARTIAL。
- [ca-skill-compiler PR #4](https://github.com/odango-chan/ca-skill-compiler/pull/4)：已收敛为仅 Compiler 的 v0.1 设计，尚未实施。

`make verify` 执行旧源码卫生检查和 v1alpha4 规范文档结构 lint/负例回归，不调用旧 Toolchain，也不代表 Compiler/Runtime/Owner 验收通过。

`skills/` 下其他历史 Skill 保持原样，不属于当前 5GC 语法基线。
