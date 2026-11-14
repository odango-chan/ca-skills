# CA-SL v1alpha3 诊断索引与 PSI 身份来源勘误记录

**文档性质：** 冻结后规范性条款的编辑性澄清及资料性测试追溯记录  
**适用版本：** CA-SL vNext / API v1alpha3（FROZEN）  
**变更分类：** §45.1 A 类索引勘误、B 类已冻结规则适用位置澄清  
**产品符合性：** NOT QUALIFIED  
**规范性依据：** [CA-SL 完整规范](../skill-language-spec.zh-CN.md)

## 1. 诊断索引现状

附录 H 定义诊断的规范性 `(Code, Phase)` 分类，**不表示其中列出的 E 用例已作为可执行 Fixture 通过**。本轮复核后的诊断索引共 99 行，分类状态如下：

| 覆盖状态 | 数量 | 含义 |
|---|---:|---|
| 规范用例已定义 | 60 | 存在可引用的附录 E 预期；不代表测试已执行 |
| 部分覆盖 | 16 | 仅有通用/间接/局部用例，尚缺当前 Code+Phase 的独立验证 |
| 待 Fixture | 23 | 缺少精确触发输入及机器执行结果 |
| 合计 | 99 | 诊断分类条目，而非测试通过数 |

此前评审指出的 `LANGUAGE_TARGET_UNSUPPORTED→E01`、`DUPLICATE_ID→E105`、`DEPENDENCY_SNAPSHOT_MISSING→E04`、`SCHEMA_MISSING→E04`、`CONTROL_FLOW_CYCLE→E60` 等错误映射已在前两轮勘误中改为待补独立用例；E115/E116 亦已移除。现行规范中不存在 E115/E116 的正式编号引用。新一轮具体修订：

- `NODE_ID_RESERVED` 补充了明确触发该诊断的 E34（并保留 E56）。
- `RECONCILE_CONTRACT_INVALID` 补充 E59、E78（保留 E60、E107）。
- `EVIDENCE_GUARANTEE_LINK_INVALID` 补充 E46、E68、E109（保留 E38、E102、E106）。
- 运行期 `EFFECT_MISMATCH` 不再引用仅覆盖静态链接的 E07/E107；改为待独立 Runtime Fixture。
- 附录 H 追加**覆盖状态**列，并以 (Code, Phase) 定义条目身份。Fixture 追踪详见 [诊断 Fixture 缺口登记](../fixtures/ca-sl-v1alpha3-diagnostic-fixture-gaps.yaml)。

该登记列出 39 个候选诊断用例，**仅包含待实施的输入变更说明和既有预期**；不提供虚假的可执行源码、测试日志或合格标记。附录 E01–E114 及 §45.2 的范围不变。

## 2. E105 的上下文解释

G.1 中 `ExportId = DottedId`，因此不合法的 `foo..bar` **始终不能作为有效 ExportId**。E105 的输入不是独立的作者源码 `ExportId` 字段；其测试位置是 `QualifiedCallableId` 等 `Alias::ExportId` 限定引用的组成部分。限定引用结构非法时，采用冻结的 `QUALIFIED_REFERENCE_INVALID`；单独的 `PredicateId`、`Alias` 等声明位置非法时采用 `IDENTIFIER_INVALID`。此处只明确诊断适用位置，**不修改 E105 的诊断结果**，也不允许非法词法输入通过构建。

若后续发现存在一个真实可独立声明 ExportId 的作者语法位置，并且其期望诊断与上述规则产生冲突，则需单独复核 §45.1 C 类变更；不能借本记录改变冻结的 E105 预期。

## 3. §13.3 与 5GC PSI Scope

§30 的 `context.request.pduSessionId` 是**请求选择参数**，而不是具有身份权威的 SourcePath。教学 Owner 的有效授权 Scope 仍须由 Host 的受信 UE/Lifecycle/入口绑定及权威 Owner 的 Session/PSI 资源关联证明组成，并核对请求 PSI 的一致性；这符合 §23 的多 Session/PSI 隔离要求。仅以 UE Ref 授权整个会话集合或凭请求 PSI 自报建立 Scope 均不满足这一前提。

真实 Owner 或部署策略若把 `pduSessionId`、DNN、S-NSSAI 定义为身份或授权实参，则直接使用 `context.request.*` 的调用仍按 §13.3 报 `CALLABLE_ARGUMENT_PROVENANCE_INVALID`。必须改用 Host 已验证的 Session/PSI Context 投影或权威 Producer 输出。教学前提不证明现有 5GC Owner 发布物已经具备这些投影；§45.2 的实际迁移/运行验收仍有待完成。

## 4. 尚未闭合的诊断可表达性

当前 YAML 源码使用映射表达 Node ID 及 `routes`。在严格拒绝重复 YAML Key 的前提下，`DUPLICATE_ID` 与 `CONTROL_FLOW_AMBIGUOUS` 的某些直观负例可能在语法阶段被 `YAML_PARSE_ERROR` 先行拒绝，无法独立触发对应诊断。

此问题**未通过修改诊断优先级解决**。候选清单已将这两个条目标为“须复核语法可表达性”。后续须提供不依赖非法重复 Key 的可构造输入，或评审是否需要在新的语言/诊断版本中调整分类。未完成该审查前，不得声称所有诊断已有可执行 Fixture。

## 5. 不变边界与验收要求

- 未改变 G.1 的标识符文法、E105 的既有诊断结果或 v1alpha3 语言目标。
- 未放宽 §13.3 的身份来源规则，也未将请求字段提升为受信 Session/PSI 身份。
- 未改变 Reconcile 的 `recoverableOutputSchema`、Mutation Outcome、Capability/Effect、Scope 或终态语义。
- 本轮不创建 E115/E116；新候选采用非规范性的 DFX 索引。
- 附录 H 保持诊断名称与阶段的规范性分类入口；覆盖状态与候选列表为资料性索引。
- 真正的 Compiler Native/WASM、Studio、Runtime、Owner 发布物及真实 5GC 验收仍需按照 §45.2 独立提供证据。

本次勘误不宣称实现符合性，也**不宣称 39 项缺口已全部解决**。若后续需要改变规范性诊断结果或增加可接受的身份来源，应按 §45.1 C 类流程升级版本。
