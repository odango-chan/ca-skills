# ConnectionAgent Skills

[English](README.md)

ConnectionAgent Skill Language（CA-SL）定义 Skill 如何声明输入、调用工具，以及验证业务目标是否达成。本仓库发布语言规范、编写指南和 Skill 示例。

## 当前版本

**CA-SL v1alpha5**（`connectionagent.io/v1alpha5`）是当前冻结版本。[发布记录](docs/releases/ca-sl-v1alpha5.md)提供规范与配套 IngressCatalog 契约的固定提交链接，并记录编辑性勘误。

- 查阅[语言规范](docs/skill-language-spec.md)，了解语法与语义。
- 参照[编写指南](docs/authoring.zh-CN.md)编写 Skill。
- 通过[文档索引](docs/README.md)查找 Schema、诊断注册表和历史资料。

## 示例

| Skill | 展示内容 |
| --- | --- |
| [传统 5GC PDU 会话](examples/skills/establish-pdu-session/SKILL.md) | UE 请求的会话建立流程，包含入站事件等待和最终 Postcondition。 |
| [OpenAMSM MAS PDU 会话](examples/skills/establish-pdu-session-mas/SKILL.md) | 基于 OpenAMSM NW Agent 计划的策略优先会话流程。 |

[示例](examples/README.md)用于展示 v1alpha5 源码写法。链接和运行需要可信 Owner 契约及部署绑定，产品符合性状态见发布记录。

## 本地验证

准备 Git、Make 和 Python 3.11，然后运行：

```sh
git clone https://github.com/odango-chan/ca-skills.git
cd ca-skills
make verify
```

该命令检查仓库源码、规范结构和 Wait／Ingress 注册表。

## 参与贡献

提交 [Issue](https://github.com/odango-chan/ca-skills/issues) 时，请注明 CA-SL 版本、涉及的条款或示例，以及预期行为。提交 PR 前请运行 `make verify`。

## 许可证

仓库级许可证待定。
