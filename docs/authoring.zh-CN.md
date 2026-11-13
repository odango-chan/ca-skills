# ConnectionAgent Skill 编写指南

**语言权威：** [CA-SL vNext 综合规范](skill-language-spec.zh-CN.md)。本指南只做导航，不另行定义语法。

## 1. 当前正式源码基线

当前 5GC 可执行 Skill 仍以 v0.2 为业务行为基线，尚未完成 vNext 迁移。MAS 是设计候选，不是第一阶段真实执行验收基线。迁移前不改写现有可运行源码。

## 2. vNext Skill Package

~~~text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/<case>/case.yaml
├── references/
├── schemas/
└── scripts/
~~~

三个 assurance 文件各司其职：

- `contract.yaml`：Skill 的公共声明，包括 Goal、公共 Request Schema、Host Invocation Context Schema、公共依赖身份和 Capability Grants。
- `procedure.yaml`：唯一执行图，包括start、Precondition / Operation / Observation / Postcondition 节点、路由和最终验收。
- `predicates.yaml`：可复用 Predicate 的参数签名和 CEL / Python evaluator。

**Contract 保留为作者维护的源码。** 只移除冗余包装字段和可由其他信息确定的字段，不删除它承载的公共声明。Compiler 可从 Contract、Procedure、Predicate 和依赖快照生成规范化 Runtime 契约，但不以生成物取代作者源文件。

## 3. Contract 保留什么

| 字段 | 处理 |
|---|---|
| `goal` | 保留，声明业务目标 |
| `requestSchema` | Skill 自有的公共请求 Schema |
| `contextSchema` | Host 发布的精确 Invocation Context Schema |
| `dependencies` | 别名 → 稳定包 ID 字符串 |
| `capabilities` | Skill 请求授权的 Capability ID 列表 |
| `apiVersion`、`kind` | 不写入源码，由 Compiler Target 和文件结构确定 |
| `metadata.name` | 由 Skill Package 根目录确定 |
| `entryProcedure` | 单一 Procedure 入口，不需要重复字段 |
| `postconditions` | 最终 Postcondition 在 Procedure 用 `postcondition.goal` 对应 Contract Goal；各成功路径可以由不同节点证明 |
| `planning.allowDynamicProcedure` | 静态 DAG 规则已禁止动态执行图，无需重复 |
| `planning.maxActions` | 旧字段取消；可选 `limits.maxActions` 只设 Skill 更严格的上界，Host 必须另有正数预算且不可被放宽 |
| `failureSemantics.outcomeUnknown.requireReconcile` | 作为 Mutation UNKNOWN 的通用安全规则，不由每个 Skill 重复开关 |

依赖身份与 Capability Grants 不是一回事：依赖让 Studio / Compiler 获得并链接 Owner 契约；Grant 才是授权请求。依赖存在不等于有权执行，Grant 也不能替代 ToolCatalog / Schema 依赖。

## 4. Skill Studio 创建流程

创建 Skill 时，Studio 应提供引导式选择，而不是让作者手工填写一堆 Owner ID：

1. 从公共依赖目录选择 Host Context、ToolCatalog、Observation 和共享 Schema。
2. 选择 Host 发布的 Invocation Context Schema。
3. 从可信 CapabilityContracts 选择允许请求的 Capability。
4. 创建或选择 Skill 自有 Request Schema。
5. Studio 生成 / 更新 `contract.yaml`；编写 Procedure 时再绑定具体导出接口。

后续可在 Dependencies / Capabilities 视图继续调整。Studio 获取精确依赖快照并作为 Build 输入传给 Compiler。Compiler 只解析、链接和校验，不联网下载或管理依赖版本。

Contract 将依赖 Alias 映射到稳定 Package ID。Compiler 按别名和实测摘要核对可信构建调用方提供的包身份和 Owner，再链接精确导出。复用已有快照，无须额外的发布 Manifest。Contract 不保存下载位置、版本锁或 digest；Schema ID 中已有的不可变版本标识仍须保留。

## 5. 其余规范入口

请以 CA-SL 综合规范为准，重点阅读：

1. 概念模型与所有权边界；
2. Contract、Dependency 与 Capability Grants；
3. Procedure 四种节点、入口 / 最终门禁和 DAG；
4. Predicate.parameters 与显式 arguments；
5. ToolCatalog、Observation、Evidence 和 Schema 所有权；
6. Procedure Script 与 Predicate Script；
7. PDU Session 示例、异常场景和 FAQ。
