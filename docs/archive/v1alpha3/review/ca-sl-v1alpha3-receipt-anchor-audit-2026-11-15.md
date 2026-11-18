# CA-SL v1alpha3 — Receipt 通道锚点与规范权威性审计

**日期：** 2026-11-15  
**适用版本：** CA-SL vNext / API v1alpha3  
**性质：** §45.1 A/B 类，既有逻辑通道根与示例的一致性澄清；不重新定义 Reconcile 或迁移到新路径语法  
**产品状态：** NOT QUALIFIED（不以文本审计替代 §45.2 测试）  
**唯一 Normative 正文：** [中文规范](../../../skill-language-spec.zh-CN.md)

## 1. Receipt/Proof 根裁决

此前 §9.2.1、F.1、G.2.1、G.2.2 均使用 `receipt.commit` 等路径；G.2.1 给出的 `create-receipt` / `reconcile-receipt` Schema 根却直接含 `commit` 而不含 `receipt` 字段。若把完整 SourcePath 的每段直接压入 Schema 根，会产生不可链接的假错误。

按已有实例与“Owner 输出/证明双通道”规则，冻结的**解释**为：

1. 受认证的 Owner 返回逻辑表示分为 `output` 和 `receipt` 两个通道；它们不是同一份 Schema。
2. `receiptSchema.$ref` 描述 `receipt` **通道对象根**；`outputSchema.$ref` 描述 `output` **通道对象根**。二者不包含逻辑通道首段。
3. Proof/failureClass 路径以 `receipt.` 为逻辑选择前缀，Compiler 剥离此前缀，从对应 receiptSchema 根解析其余字段和证明 Schema；恢复路径同理剥离 `output.`，从调和 READ 的 outputSchema 根解析。
4. 同一调用必须各自验证 Source Identity、Owner、Scope、Correlation 和证明关联，不能把原 Mutation receipt 代替 Reconcile READ receipt。真实 Provider 的物理传输 Envelope 由版本化 Owner 协议定义，并由受信边界解码；不要求现实 HTTP 回包必须就是示例 YAML 形状。
5. `reconcile-receipt.schema.yaml` 的示例根含 `commit`，因此 `receipt.commit` 正确；`receipt.receipt.commit` 在**该例**不存在第二段 `receipt`，静态拒绝；不能悄悄补 Schema 包装层或删改路径。其他 Owner 若在 Schema 中真实定义同名嵌套字段仍按实际 Schema 精确校验。

**不采用的修订：** 把全部 `receipt.commit` 改为裸 `commit`，或给 `receiptSchema` 再加一层 `receipt` 属性。这两者会改变现有路径/Schema 的接受语义，按 §45.1 C 类需要互操作版本评审，不能当作普通勘误。

## 2. 字段级验收与诊断

- 正例：G.2.1 `reconcile-proof:v1` 约束 `originalInvocationId` / `commitState`，同一 READ 的 `output.recovered` 以 `create-output:v1` 校验。Runtime 先校验 receipt 所证实的原 Mutation，COMMITTED 时才给 Procedure `reconcile-node.operation.output` 暴露已验证恢复对象；Evidence 保留 `example.session.reconcile` READ 的真实 Producer kind/outcome/Invocation ID。
- 静态反例：当前 Reconcile receiptSchema 根仅含 `commit`，把 proofPath 改为 `receipt.receipt.commit` 或把证明路径写成无锚点 `commit`，必须拒绝而不是重写；对 G.2 正确调和契约的错误路径使用既有 `RECONCILE_CONTRACT_INVALID`。
- Runtime 反例：真实回包缺失 `receipt.commit`、`originalInvocationId` 与持久化调用不符、commitState 来源不可信或恢复 Schema 无效，均不得从返回值或 `output.recovered` 推断原 Mutation 成功；分别按 §20.1/§20.3、§24.2 走已有安全停止或 UNKNOWN/Reconcile 路径。若已确认提交而承诺恢复无效，记 `COMMITTED_OUTPUT_UNAVAILABLE`。
- 补充资料性 DFX 候选，保持 E01–E114 的预期范围，不声称机器 Fixture 已执行。

## 3. 其余评审项的状态

| 评审项 | 核对结果 | 处置 |
|---|---|---|
| §13.3 身份实参标注 | F.1 已冻结最低抽象属性；真实 ToolCatalog 物理字段仍未交付 | 维持独立 Owner 互操作发布物的版本化条件，不添加 `identityInputs` |
| §22 / H / E 的重复表格 | §22.1 已作为路由矩阵权威来源；H 的 `(Code, Phase)` 分类为 Normative，E 的明确预期仍有 Normative 效力 | 补权威层次说明；**不**把 H/E 整体降为 Informative |
| E115 / E116 | 当前规范中均无正式编号引用；现有冻结范围 E01–E114 | 不重编号，不虚构 Fixture |
| Schema 组合关键字 | F.5/G.4 已拒绝 `allOf/anyOf/oneOf/not/if-then-else`；仅 `type: [T,"null"]` 为允许的 nullable 类型形状 | 补充清晰度；Schema 自身非法先于合法 Schema 的静态赋值失败 |
| 阶段 Outcome、诊断及 Invocation 终态 | 各枚举及 Owner/Runtime 来源已由 §22、§22.1、§20、§24、H 约束 | 增加资料性总览表；任何行为以相应规范性条款为准 |
| G.2 Evidence Producer 映射 | 已有抽象规则、缺字段级合成示例 | 补字段级 COMMITTED 正例与错误锚点、错误原调用反例 |
| §45.2 | 已有 Compiler/Runtime/Studio/Owner 的分层矩阵和 8 项门槛 | 原样保持，产品均 NOT QUALIFIED |

## 4. 修订边界与仍未完成的事

这次没有新增 SourcePath、Effect、Capability、ToolCatalog v1alpha3 字段、BuildRequest 字段或新的路由/终态，也没有提升请求字段权威性。Owner 身份标注的**物理发布格式**、跨发布物 Reconcile 专用身份绑定、Provider 物理 Envelope 如何认证地映射到双通道，以及可执行 Fixture/CI 属于尚未验收的外部交付条件；无法提供受信输入则必须 fail-closed。

如果实际实现的 Owner wire format 强制把 `receiptSchema` 理解为整个 Envelope 的 Schema，或与本文的逻辑双通道不兼容，那么不应该假装 v1alpha3 勘误已让它通过；需要在其 Owner 互操作协议版本中显式定义迁移并重新验收。现有 Core Language 继续 FROZEN，产品始终 NOT QUALIFIED。
