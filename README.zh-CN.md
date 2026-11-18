![ConnectionAgent Skills](assets/repo-banner.svg)

# ConnectionAgent Skills

[English](README.md)

ConnectionAgent Skill 官方源码与 CA-SL 语言规范。**CA-SL v1alpha5 已冻结。** 下游可通过[发布记录](docs/releases/ca-sl-v1alpha5.md)锁定规范与配套 Ingress 契约。

| 入口 | 内容 |
| --- | --- |
| [语言规范](docs/skill-language-spec.md) | 当前 CA-SL 目标、配套契约及历史版本 |
| [编写指南](docs/authoring.zh-CN.md) | Skill 包结构、Procedure、Predicate、Schema 和 Script |
| [PDU 会话示例](examples/README.md) | 传统 5GC 和 OpenAMSM MAS 的 v1alpha5 源码示例 |
| [仓库文档](docs/README.md) | 编写参考、历史基线及设计归档 |

示例需要可信 Owner 契约才能完成链接，产品状态为 `NOT_QUALIFIED`。[历史 Skill 包](skills/README.md)和[导入快照](lib/README.md)保留原路径，供现有消费者使用。

运行 `make verify` 检查源码、规范结构及 Wait／Ingress 注册表。Compiler、Runtime 和真实 5GC 由各自的验收测试验证。
