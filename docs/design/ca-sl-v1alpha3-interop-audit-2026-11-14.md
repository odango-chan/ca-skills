# CA-SL v1alpha3 — 互操作审计与符合性分流澄清（2026-11-14）

**性质：** 冻结后 A/B 类解释性修订及尚未关闭的互操作交付缺口登记；本文件不新增语言字段或改变现有 E 用例预期  
**权威文本：** [CA-SL v1alpha3 中文规范](../skill-language-spec.zh-CN.md)  
**状态：** 语言语义 FROZEN；独立 Owner 互操作发布物和 Compiler/Runtime/Studio 符合性仍为 **NOT QUALIFIED**

## 评审逐项裁决

| 评审项 | 已核对的 main 状态 | 本轮修订/剩余条件 |
|---|---|---|
| F.1 / §13.3 身份实参 | §13.3 已规定 Owner 身份路径标注、部署 Scope 策略路径并集及双阶段 provenance 诊断；F.1 无 `identityInputs` 物理字段 | F.1 补齐已有要求的最小**逻辑属性**，但不制造 ToolCatalog 物理字段。Owner 必须有受信且可消费的发布契约，未交付时不能声明互操作符合性 |
| F.4 `IndependentDomains` / factIdentity | §34.0.2、F.4、G.3.1 已规定部署、发布者、摘要、独立域对、共同事实、Scope 映射、Schema 及缺失拒绝 | 已解决规范逻辑属性；物理 BuildRequest / Deployment 绑定仍需版本化发布及机器验收 |
| G.2 Reconcile 防绕过 | 禁止普通 `operation.target` 绕过原调用检验，但缺少明确的同快照检测位置 | 本轮规定在**所有受信 ToolCatalog 导出**中检索 Mutation 的 `mutation.reconcile.callable`，识别同快照专用 READ，并拒绝普通调用；跨快照身份仍需 Owner 互操作契约 |
| Appendix H / E115、E116 | 已在先前勘误中校正错误映射；H 使用 `(Code, Phase)`，E115/E116 非正式 E 范围 | 不重复改 H；诊断的机器 Fixture 仍未运行，继续以现有缺口登记追踪 |
| §45.2 工具职责分流 | 已有 E01–E114 规范预期和资料性 `proposedExecutionClass` 机器追踪文件 | 新增按**用例变体**而非编号范围的 Compiler/Runtime/Studio/Owner 分层验收说明 |
| §12.9 Goal mismatch | §24.1 已有专用诊断，§12.9 已要求 Goal 精确匹配 | 明确在图证明传播之前拒绝显式不匹配的 Goal |
| F.4 `exportKind` | E39/E43 已使用 operation/observation/schema/evidenceGuarantee 既有类别 | 将四种已链接导出分类并置于 F.4，Host Context 仍是 Schema，Reconcile READ 仍是 operation |
| F.6 `Annotated` | G.4 已有限定的 JSON Schema 支持子集；F.6 原有 `Annotated` 映射限制 | 补充 `minLength` 正例与 `pattern` 非法反例；不得由 Python typing 支持范围推导出额外 Schema 支持 |
| §10.1 Node 非空、§20.1 阶段 SUCCEEDED、H 同名多阶段 | 正文已分别明示非空阶段、路由脚注和 `(Code, Phase)` | 不重复改已有规则；避免引入无效差异 |

## 最关键的互操作交付缺口（不伪装为 v1alpha3 编辑勘误）

### A. 可消费的 Owner 身份输入描述符

§13.3 必需的身份标注至少需要 `owner/kind/id`、身份维度、精确输入子路径、与该 callable Input/QueryContext Schema 的可信对应，以及发布者授权与当前 Scope 关联。**这些是现有逻辑要求，不意味着 `ToolCatalog/v1alpha3` 已存在相应 JSON/YAML 字段。**

下列仅为未来 Owner 互操作契约的**提案示意**，不是 v1alpha3 许可字段：

~~~yaml
# NON-NORMATIVE, NOT AN EXISTING TOOLCATALOG/v1alpha3 FIELD
identityInputs:
  - dimension: session
    path: arguments.pduSessionId
~~~

若发布新物理字段、改变 Owner 线格式或调整可接受的合法输入，应走 §45.1 C 类的独立互操作协议版本升级；不得静默在 v1alpha3 ToolCatalog 上添加必填项。E101 的静态与 Runtime Fixture 需要与真实发布格式一致后才能验收。

### B. Reconcile-only 跨快照、跨 Skill 专用身份

在已验证 ToolCatalog 快照内，可从所有 Mutation 的 `mutation.reconcile.callable` 关系识别专用 READ，并在普通 `operation.target` 引用时阻断。**不能仅在当前 Skill 引用的 Mutation 子集中查找**，否则另一个 Skill 可以绕过。

对不在同一可信快照内的 Reconcile 关系，缺乏 Owner 的认证发布关系时不得从字段名或输入 Schema 自行推断。若最终需要新增 `reconcileOnly` 等专用标记或改变 Owner/Runtime 权限判断，应升级相应互操作契约版本并增加独立测试，不得假装 v1alpha3 已支持该字段。

### C. 精确 `Annotated` 元数据映射的外部实现剖面

G.4 的支持关键字集合已经冻结；`pattern`、`format`、组合断言不得接受。真实 Python AST → Schema 派生的元数据字典物理表达、非法组合、完整类型约束映射需要 Compiler 与 Script Contract 给出同一套机器 Fixture。未来若要扩大支持集合或改变原定拒绝行为，按 C 类升版，不在本次编辑性修订中引入隐式解释器行为。

## 测试责任与追踪

- 附录 H 的诊断身份为 `(Code, Phase)`，不同阶段的 `EFFECT_MISMATCH` 不合并。既有 [诊断 Fixture 缺口登记](../fixtures/ca-sl-v1alpha3-diagnostic-fixture-gaps.yaml) 的候选均不能当作已运行测试。
- [E01–E114 追踪表](../fixtures/ca-sl-v1alpha3-case-traceability.yaml) 已有逐用例 `proposedExecutionClass`；§45.2 新矩阵说明产品职责，两者须一起使用。不可把 E23/E28/E31/E58/E96/E97 等 Runtime 结果虚构为 Compiler CI PASS。
- Reconcile 同快照普通调用负例已增补为资料性 DFX 候选，不改变 E107 已冻结的预期。
- 审查、YAML 文本更新、GitHub PR 通过不代表 Compile/Runtime/Studio、Owner、真实 5GC 符合性通过。

## 冻结边界

本轮只关闭既有规则的可发现性、同快照判定位置、诊断优先级及验收分工，不新增 SourcePath、Effect、Capability、Host 字段、ToolCatalog 物理字段或 BuildRequest 字段。**CA-SL v1alpha3 核心语义维持 FROZEN；可操作的 Owner 互操作发布物及机器符合性证据仍待补齐，产品保持 NOT QUALIFIED。**

若后续评审证明任何本轮解释改变了合法输入集合、原定诊断或执行安全结果，则该项必须回退并按 §45.1 C 类升级，不得继续以编辑勘误名义合入。
