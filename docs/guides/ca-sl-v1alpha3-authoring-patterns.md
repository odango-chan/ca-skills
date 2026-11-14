# CA-SL v1alpha3 作者指南：SourcePath、Evidence 与 Owner Schema

**性质：** 资料性作者指南（Informative）  
**适用版本：** CA-SL vNext / API v1alpha3  
**规范性依据：** [CA-SL 完整规范](../skill-language-spec.zh-CN.md)

本指南说明符合现有规范的常见写法，不增加新的语法、缩窄规则或权限来源。任何示例中没有给出完整 Owner 发布物的引用，均表示模式说明，**不是已通过 Compiler 的独立 Fixture**。

## 1. SourcePath 与可选字段

SourcePath 的直接绑定只允许引用在该路径所有可达分支中**保证存在**的字段。即使此前某个局部 Predicate 返回 PASS，也不将 Owner Schema 的 `NotRequired` 字段自动收窄为必需。

建议按以下顺序处理：

1. 若字段在 Owner 成功结果中始终存在，由 **Owner** 将其发布为 required，并经对应精确 Schema ID 重新链接；Skill 不应复制或修改 Owner Schema。
2. 若属性合法但可缺失，将其必定存在的**外层对象**绑定给类型可检查的 Procedure Script，由 Script 显式处理缺失，并返回符合其严格 TypedDict 返回契约的结果。
3. 若字段涉及 Subject、Session/PSI、Lifecycle、Correlation 或资源句柄的身份，Procedure Script 的派生值**不得**作为授权身份来源；应使用受信 Host 关联投影或权威 Producer 的直接输出（§13.3）。

**禁止的推论：** Predicate PASS 不能单独证明后续 SourcePath 一定存在，也不赋予 Script 创建的标识符以身份权威。

## 2. Evidence 更新与长流程验收

已接受的 Evidence 有明确 Producer、Scope、Correlation、时间和事实来源。新 Evidence 即使包含相同业务值，也可能使旧的 PASS 不再适用于当前执行状态。

推荐的受控流程为：在受保护的 Mutation 派发前或最终成功发布前，按业务要求显式调用获授权的 Observation；将**本次新产生的 Producer output**及其 Evidence 绑定至新的 Predicate；取得新的 Goal Postcondition PASS 后，继续通过 Runtime 的准入和成功发布复核。

不得将旧 Predicate 的参数隐式替换为更新值，不得把普通 Operation Result 冒充 Observation Result，也不得以“有 Evidence Ref”代替保证验证。当前规范的示例与预期参见 E30、E40、§17.2 与 G.8。

## 3. 独立性保证的错误分类

静态无法解析受信身份域、共同事实绑定、Scope 映射或授权时，构建被 `EVIDENCE_GUARANTEE_LINK_INVALID` 阻断。绑定全部合法但能从静态声明证明无论何种合法记录均不能组成独立证据时，报 `PREDICATE_EVIDENCE_UNSATISFIABLE`。当静态可满足而本次记录缺失、过期、同源或无法核验时，Predicate 返回 UNKNOWN。

见 [统一决策索引](../design/ca-sl-v1alpha3-decision-and-trace-index.md)和 §G.3.1。

## 4. Owner Schema 投影的发布与版本治理

v1alpha3 允许 Owner 为不能直接落入受支持 JSON Schema 子集的业务对象另行发布**符合该子集的受信投影**，但这不授予 Skill 自行修改外部数据结构的权限。

投影的可信性依据来自既有规则：发布方必须是对应数据/接口的权威 Owner；投影须有独立、精确且可链接的 Schema `$id`，并作为可信快照的文件字节纳入 Package ID、Owner 归属、摘要及构建依赖身份校验（§7、§34.0、F.4、G.4）。原结构的版本变化、字段删除或语义改变需要由 Owner 重新审查相应投影是否仍然正确。Compiler 只能验证已发布投影的 Schema、链接和类型；**不能仅凭形式上的 Schema 兼容推断它在业务上等价于原结构**。

如果部署需要显式的“原结构 ↔ 投影等价性”签署、源版本字段或新证据证明，这属于 Owner/互操作契约的新增发布要求；其线格式与授权方式应单独版本化，不得通过 Skill 注释、README 或无来源的转换结果代替。当前规范没有为此定义额外的强制签署字段。

## 5. CEL、Python 与 Schema 的实现版本

G.4 与 F.6 已限定允许的表达式、类型和注解集合。不得因为某个 CEL 引擎或 Python 解释器支持更多语法，就自动在 v1alpha3 中接受这些语法。

参考实现可以选择 Python 3.11 及其标准库 `typing.Required`/`typing.NotRequired` 支持；这不是冻结语言对运行环境新设的最低版本。实际产品须在 §45.2 的验收记录中注明 CEL parser/evaluator、Python AST/typing 分析器、Python 执行环境及 JSON Schema 解析器的确切版本或源码提交，针对相同输入提交原始结果与诊断，证明 Native/WASM/Studio 的一致性。

`$defs`、`definitions`、本地 JSON Pointer 引用及循环引用在 v1alpha3 的 G.4 闭合白名单之外，不得作为实现扩展。有关是否在后续版本允许这些写法，应提交独立的语言契约修订。

## 6. 适用的验收记录

本指南本身未通过 Compiler、Runtime 或真实 5GC 测试。正式验证仍遵守 §45.2 的八项门槛以及 [E01–E114 预期索引](../fixtures/ca-sl-v1alpha3-case-traceability.yaml)。作者不得将资料性写法作为现行产品已支持的声明。
