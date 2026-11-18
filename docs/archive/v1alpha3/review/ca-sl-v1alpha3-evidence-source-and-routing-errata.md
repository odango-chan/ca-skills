# CA-SL v1alpha3 — Evidence 来源、运行路由与 Schema 闭合性勘误

**类型：** 冻结后 A/B 类文本勘误和既有规范性约束的解释性闭合  
**版本：** CA-SL vNext / API v1alpha3（语言 FROZEN）  
**产品验收：** §45.2 NOT QUALIFIED  
**规范性来源：** [CA-SL v1alpha3 完整规范](../../../skill-language-spec.zh-CN.md)\
**回归计划：** [RFX-117–RFX-122（资料性候选，不是正式 E 用例）](../fixtures/ca-sl-v1alpha3-review-regression-candidates.yaml)

## 1. 评审发现与处置

| 评审项 | 已有规则与核验 | 本轮处理 | 分类 |
|---|---|---|---|
| §13.3、§30 的 Request PSI 身份 | 前几轮勘误已禁止以 `context.request.pduSessionId` 直接作为 Session/PSI 身份；教学 Owner 只将其作为选择输入，真实 Scope 必须经受信 Host/Owner 绑定 | 补充 `context.session.psiRef` / `context.correlation.pduSessionRef` **仅为 Host 已正式发布时可用的候选示意**，并未在语言中新增该字段或承认教学样例已获真实 Owner 授权；回归候选 RFX-117 | B |
| §17.1 的 requires 与来源豁免 | 已列出的每项保证必须满足；来源豁免原本只允许在所有调用点均可豁免时**省略声明** | 明确**显式 requires 不被豁免来源消除**；静态无法满足 → PREDICATE_EVIDENCE_UNSATISFIABLE，Runtime 缺少有效记录 → UNKNOWN；混合调用点却省略 requires → PREDICATE_EVIDENCE_REQUIRED；回归候选 RFX-118 | B |
| §24.2 / H 的 Scope/Correlation | §24.2 将派发前授权交集为空与已派发回包校验失败分开；前者可能走 DENIED，后者不得视为未授权请求 | 明确 READ/Observation 回包不匹配时隔离、走已声明 UNKNOWN 或停止；Mutation/Reconcile 按 §20；H 两行同步，RFX-119 | B |
| §F.5 / G.4 组合 Schema | G.4 白名单排除了 allOf/anyOf/oneOf/not/if…，§F.5 原含“可证明的组合可接受”的不一致表述 | 删除对组合可接受性的暗示，固定 G.4 白名单之外一律 SCHEMA_INVALID，只有合法 Schema 之间不可赋值才可能 INPUT_TYPE_MISMATCH；§34.1 不再笼统写“组合”；RFX-120 | A/B |
| IndependentDomains / factIdentity 线格式 | §34.0.2、F.4、G.3.1 已规定可信逻辑属性，具体 BuildRequest 传输字段仍归外部版本契约所有 | 重申由 Deployment 的信任工件契约和受信 BuildRequest 版本共同定义物理字段，Compiler 验证既有逻辑闭包；不发明新字段；RFX-121 | B |
| `pendingResponsibilitiesRetained` 与 PENDING | §20.1.1、G.5 已明确有任一确认 PENDING 时必须 SAFE_STOPPED，Goal PASS 不绕过终态保护 | §29 明确该布尔值表示**责任记录仍被保全**，不代表 PENDING 已消除；本地 Goal PASS 和真实 Invocation 终态分离；RFX-122 | B |
| EFFECT_MISMATCH 与历史 E 映射 | H 已采用 `(Code, Phase)`；错误映射与未定义 E115/E116 已在 PR #27–#32 修复 | 不拆分或改名原 Code；不重复修正历史评审引用 | A |
| §12.9、§20.2 与文档标题 | §12.9 已有“matching Goal Postcondition”概念，§20.2 已有路径覆盖规则 | 伪代码明确 `postcondition.goal == contract.goal && PASS`；补 retryOf 直达/调和正例和绕过负例；增加第八部分标题，统一“本版（v1alpha3）” | A |

## 2. 显式 Evidence 优先级的判定依据

本轮**不采纳“来源豁免优先于已经声明的 requires”**的建议。该做法会使作者显式声明、Owner 发布的保证在部分调用点被跳过，违背 §17.1 中“每个列出的保证至少由一条有效 Evidence Ref 满足”的要求，构成减少必要证据的语义变更。

维持现有规则可得：

- 若参数所有调用点均来自可豁免来源，且没有声明 `requires`，可通过来源检查，仍需满足业务 Goal 的权威证据要求。
- 只要存在不可豁免的调用点，省略相应 `requires` 就是 `PREDICATE_EVIDENCE_REQUIRED`。
- 一旦显式声明 `requires`，任何调用点都不得因来源可豁免而跳过该保证。静态上不可能满足时为 `PREDICATE_EVIDENCE_UNSATISFIABLE`；运行时实际证据不足时 Predicate 为 `UNKNOWN`。

如果后续提出“同一参数某些调用点不需要已声明保证”的新语义，须经 §45.1 C 类版本化评审，并给出授权/Evidence 安全证明，不能在本勘误中引入。

## 3. Scope 错误发生阶段

当失败发生在**派发前**，部署授权 Scope 交集为空报 `SCOPE_INTERSECTION_EMPTY`；普通 callable 可按已声明 DENIED 边处理。当失败来自**已派发 Owner 结果**与要求的 Scope/Correlation 不匹配，该结果不得作为有效业务事实使用，也不得把它重分类为可继续执行的授权拒绝。READ/Observation 根据 UNKNOWN 边处理或停止；Mutation/Reconcile 根据已派发原调用的独立证明确定提交状态，保留责任。

本轮同步 §24.2 与附录 H 的两条 Runtime 处置描述；未更改诊断的规范性 `(Code, Phase)` 身份。

## 4. 用例编号与验收范围

正式规范预期仍为 **E01–E114**。评审建议的 E117–E122 已转为 **RFX-117–RFX-122** 资料性回归候选，不新增规范性用例编号，也不声称已有编译器、运行时或真实 Owner 的机器执行证据。有关新 E 编号的采用必须经过后续符合性用例评审和 §45.2 范围更新。

现存 39 项诊断 Fixture 缺口和执行分类继续按各自索引跟踪；现有 Source Hygiene PASS 只能说明仓库源文件检查通过，不构成 §45.2 产品验收。

## 5. 变更边界

本勘误未修改已发布 Owner Schema、Request Schema、Capability、Scope、Evidence 保证、Mutation/Reconcile Outcome、Stage 路由或终态算法；也未允许新的 JSON Schema 组合结构。若任何实际 Compiler/Runtime 测试证明本轮澄清改变了原有冻结语义的可观察结果，应停止将该差异作为 v1alpha3 勘误发布，按 §45.1 C 类提交新版本评审。
