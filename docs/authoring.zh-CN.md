# ConnectionAgent Skill 编写指南

**语言权威：** [CA-SL v1alpha5 完整规范](skill-language-spec.v1alpha5.zh-CN.md)。本指南只做导航，不另行定义语法。v1alpha4 保持不可变历史版本；v1alpha5 语言及互操作规范已冻结。Compiler / Runtime / Studio / Integration / 5GC 产品符合性仍需按 §45.2 / §L.13.2 独立验收。

## 1. 源码示例

[v1alpha5 PDU 会话示例](../examples/README.md)提供传统 5GC 和 OpenAMSM MAS 的编写参考，完成链接需要可信 Owner 契约。`skills/` 下的原有包用于保留[历史 5GC 行为基线](current-5gc-skill-baseline.md)。

## 2. v1alpha5 Skill Package

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

- `contract.yaml`：Skill 的公共声明，包括 Goal、全局前置条件、公共 Request Schema、Host Invocation Context Schema、公共依赖身份和 Capability Grants。
- `procedure.yaml`：唯一执行图，包括 `start` 与业务 Node。业务 Node 可按顺序声明 Precondition、Operation、Observation、Postcondition。非末阶段正常完成后继续同一 Node。当前阶段的 `routes` 将 Outcome 映射为 Node ID 或 Invocation 终态，末阶段的正常 Outcome 也使用该映射。
- `predicates.yaml`：可复用 Predicate 的参数签名和 CEL / Python evaluator。

**Contract 保留为作者维护的源码。** 只移除冗余包装字段和可由其他信息确定的字段，不删除它承载的公共声明。Compiler 可从 Contract、Procedure、Predicate 和依赖快照生成规范化 Runtime 契约，但不以生成物取代作者源文件。

### Node-entry Wait（v1alpha5）

Node-entry Wait 是目标 Node 入口处的可选控制，不是第五种业务阶段，也不创建 Wait-only Node。事件被接受后，归一化请求通过该 Node 的 `wait.output` Producer 路径提供，且只在事件接受分支上可用。超时通过 Wait 自身的 `TIMEOUT` Route 处理。配对协议响应边界独立于 Invocation 最终 Goal 证明声明。

Wait 必须选择可信 IngressCatalog 依赖中的精确 Ingress Operation。作者不得声明原始 HTTP envelope、delivery ID、correlation handle、tombstone 或私有 response obligation 状态。v1alpha4 原规范不变，仍拒绝 v1alpha5 的 `wait` 语法。

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
| `precondition` | 可选**单一** `<node-id>.precondition` 阶段引用；阶段可含多个 `predicates`，整个阶段聚合 PASS 才通过全局门禁 |
| `postconditions` / `postcondition.goal` | **不支持。** 最终 Postcondition 聚合 `PASS` 必须直接路由 `SUCCEEDED`，才可证明 Contract Goal |
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
3. Procedure 的 Node 内阶段、入口 / 最终门禁和 DAG；
4. Predicate.parameters 与显式 arguments；
5. ToolCatalog、Observation、Evidence 和 Schema 所有权；
6. Procedure Script 与 Predicate Script；
7. PDU Session 示例、异常场景和 FAQ。
