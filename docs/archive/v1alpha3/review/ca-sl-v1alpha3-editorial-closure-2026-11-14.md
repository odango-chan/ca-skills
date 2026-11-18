# CA-SL v1alpha3 — 冻结后编辑性澄清（2026-11-14）

**适用文本：** [CA-SL 规范（中文唯一 Normative 正文）](../../../skill-language-spec.zh-CN.md)\
**版本与状态：** vNext / API v1alpha3，语言 FROZEN；产品/Owner 符合性 NOT QUALIFIED  
**分类：** §45.1 A 类编辑性勘误、B 类既有语义的适用位置澄清；不引入 C 类语义变更

## 裁决摘要

这轮评审不重新打开已冻结的语言设计，也不引入 `v1alpha4`。先前合并的 [诊断/PSI 追溯勘误](ca-sl-v1alpha3-diagnostic-trace-errata.md) 已将 §13.3 与 §30 的身份边界收紧，本轮补全 §31 的继承说明与其他编辑性表达。

| 评审关注 | 本轮处置 | 不变的安全语义 |
|---|---|---|
| §13.3 与 §30/§31 的 PSI 来源 | §31 显式继承 §30 教学 Owner/Host 前置条件 | Request PSI 仅作选择或比对；受信 PSI 关联和 Scope 授权必须独立存在。实际 Owner/策略将字段列为身份实参时，仍按 §13.3 拒绝不可信来源 |
| §34.0 Alias / `dependencyId` | 明确被引用的 `Contract.dependencies[alias]` 必须匹配 `snapshot.dependencyId == alias`；受信查找键是 `(dependencyId, digest)` | 不由 Package ID、同名字段或摘要自动推断、重命名或提升信任 |
| §13.2 YAML Core | 明确采用 Core 的**受支持标量子集**，保留词法验证 | 只接受小写 `true`/`false`/`null` 与受限有限十进制；不接受 `Null`/`~` 等被某些 YAML 解析器接受的形式 |
| §14 Evidence | 补 `evidence.independence` 至 G.1/G.3 的交叉引用 | 组成员仍须来自 `evidence.requires`，独立性仍须受信来源证明 |
| G.1 路径 | 给固定后缀优先识别的正反例 | 文件路径、FileSegment、安全闭包均不放宽 |
| 附录 H 映射与 E115/E116 | 复核既有勘误结论，未重编号 | H 是规范性 Code/Phase 分类，不等于已执行的机器 Fixture；E01–E114 为当前集合，历史候选 E115/E116 不属于正式用例 |

## §34.0 的明确匹配流程

1. 对 `Contract.dependencies` 声明且实际使用的每个 `alias`，只选 `dependencyId == alias` 的快照。大小写敏感，不支持隐式改名。
2. 按 `(alias, 实测 digest)` 获取可信身份绑定；可信绑定给出的稳定 Package ID 必须等于 `Contract.dependencies[alias]` 的值。
3. 缺快照、重复快照、缺受信绑定、Package ID 不匹配分别沿既有 `DEPENDENCY_SNAPSHOT_MISSING`、`DEPENDENCY_DUPLICATE`、`DEPENDENCY_IDENTITY_UNVERIFIED`、`DEPENDENCY_ID_MISMATCH` 诊断处理；不定义新的诊断类别。
4. 此规则只明确既有同一 Alias 机制的匹配条件；不新增 BuildRequest 字段、Dependency Resolver 或 Package Manager 行为。

## §13.3 的正式解释

教学示例将 `context.request.pduSessionId` 传入外部 callable 时，**只表示业务选择值**。它不能为当前 Invocation 创建已授信的 Session/PSI 身份，也不能单独授权 `(UE, Lifecycle, PSI)` Scope。教学 Owner/Host 假设存在独立的受信入口关联及资源关联验证。若真实 Owner 或部署 Scope 策略把该参数视作身份、资源句柄或授权输入，则必须改为实际发布并验证的 Host Context 身份投影或权威 Producer 输出。没有这类投影时，调用必须失败，不得依靠示例豁免。

本轮不在 CA-SL 内置 `context.session.*`，也不放宽 §13.3。真实 5GC 的 Owner 标注、Host 投影和 Runtime 拒绝行为仍需通过 §45.2 独立验收。

## 评审与验收边界

- 已复核附录 H 中 `DUPLICATE_ID`、`DEPENDENCY_DUPLICATE`、`CAPABILITY_MAPPING_MISSING`、`FINAL_POSTCONDITION_GOAL_MISMATCH` 与 `CONTEXT_SCHEMA_MISMATCH` 等映射：没有把非直接用例重新挂回这些条目；缺口继续标注“待 Fixture”。
- `UNSUPPORTED_WAIT` 与 `UNSUPPORTED_V02_SYNTAX` 已有规范诊断，但不把尚未实施的 E115/E116 宣称为机器测试。
- 本次仅修改规范文本和追溯链接；没有执行 Compiler / Studio / Runtime / 真 5GC 的符合性测试。产品状态保持 NOT QUALIFIED。
- 若未来实际要求“请求值经过 Host 准入后即自动成为外部身份实参”、隐式 `dependencyId` 重映射或其他扩大可信来源的行为，须按 §45.1 C 类独立升级语言版本，不能在 v1alpha3 内静默勘误。
