# CA-SL v1alpha3 Reconcile 与诊断索引勘误决议

**日期：** 2026-11-14  
**目标语言：** CA-SL vNext / API v1alpha3（FROZEN）  
**变更分类：** §45.1 A/B 类既有条款的字段归属、诊断身份和可执行处置交叉引用澄清  
**符合性状态：** NOT QUALIFIED  
**唯一规范性正文：** [CA-SL 完整规范](../../../skill-language-spec.zh-CN.md)

## 1. 对重复评审事项的核验

| 问题 | 当前结论 |
|---|---|
| 附录 H 引用 E115/E116 | 先前已经删除；现行 §45.2 与 G.9 均以 E01–E114 为正式编号。UNSUPPORTED_WAIT 与 UNSUPPORTED_V02_SYNTAX 的测试尚待独立 Fixture，但对应语言诊断已定义 |
| LANGUAGE_TARGET_UNSUPPORTED 误引 E01 | 当前 H 已标记为“待 Fixture”，E01 仍是正例 |
| EFFECT_MISMATCH 同名两行 | 以 `(Code, Phase)` 为规范性诊断身份；C_STATIC 和 R_RUNTIME 不可合并成单一执行处置；本轮进一步明确诊断记录须包含 Code、Phase、类别 |
| Reconcile Output Schema | §12.7 / G.2 已使用 `recoverableOutputSchema` 表示恢复子对象，不等于调和 callable 的完整 `outputSchema`；本轮未修改该语义 |
| IndependentDomains | §34.0.2 和 G.3.1 已规定最小抽象属性及可信部署关系，本轮不新增发布字段 |

## 2. Reconcile receipt 与 proofPath 的归属

**新增的 G.2 字段归属表是原 G.2、G.2.1、G.2.2 已规定“各自 Owner callable 的 receipt 根”的规范性交叉索引。** 它区分契约声明在原 Mutation 下，与实际由哪个 callable 返回受信数据：

- `mutation.commitProof.path`、`failureClassPath`、`failureClasses[].proofPath` → **原 Mutation 调用** 的 `receiptSchema`。
- `mutation.reconcile.proofPath` → **独立 Reconcile READ 调用** 的 `receiptSchema`；虽然该字段声明在原 Mutation 的 `mutation.reconcile` 对象中，但其证明必须来自调和 callable 本次响应。
- `mutation.reconcile.recoverableOutputPath` → **Reconcile READ 调用** 的完整 `outputSchema` 中的可选业务子对象；`recoverableOutputSchema` 对该子对象进行校验，且只在 COMMITTED 后可作为 Node `operation.output` 暴露。
- `commitProof.schema` 与 `reconcile.proofSchema` 可以引用同一个精确 Schema `$id`，**并不表示可借用不同 Producer Invocation 的 receipt**。

如果某实现曾读取原 Mutation receipt 的 `mutation.reconcile.proofPath`，它与此前 G.2.2 的“各自 Owner callable”以及 G.2.1 调和回包示例不符，**不能把其旧实现行为当作 v1alpha3 的另一种合法解释**。若决定改变此规则，必须按 §45.1 C 类升级语言或互操作版本，而非再作为编辑勘误。

## 3. Runtime 诊断索引的可执行分派

附录 H 的 31 条 R_RUNTIME 诊断现逐条说明适用阶段和后果。具体区分如下：

1. **派发前**：校验、Effect/Scope/授权/预算/Deadline/取消错误禁止派发。符合 DENIED 语义的普通 callable 依 §24.2 走已声明 DENIED 边；其他错误直接停止，不得将任何 fail-closed 错误替换为成功或 UNKNOWN。
2. **已派发 READ/Observation**：回包不可用或无法证明结果时，沿该阶段已声明的 UNKNOWN 边；缺少边时按 §12.8 的关键事实未决终止。
3. **已派发 Mutation**：不得以解码失败、未知 Owner Outcome、Scope 冲突或超时推断未提交；必须按 §20.1 采信可独立验证的证明，缺少时沿 OUTCOME_UNKNOWN 或按有效证明安全停止。
4. **Reconcile**：只能在原调用与独立 READ callable 的授权、证明和关联满足时映射 COMMITTED/NOT_COMMITTED；无法得到有效结论时按 §20.3 沿 UNRESOLVED 或直接安全停止，保留原调用责任。
5. **Procedure Script、Predicate、最终终态**：分别沿 Script FAILED、Predicate UNKNOWN 或 §12.8 的实际终态裁决，不允许因诊断相同而套用 Tool 的派发边。
6. **EFFECT_MISMATCH（R_RUNTIME）**：立即 fail-closed，不得借用 DENIED/UNKNOWN 路由继续。若先前存在已派发外部 Mutation，仍须保存原调用责任和独立验证的提交状态。

以上为 §24.2 既有分派规则的索引表达，不新增新的阶段 Outcome。

## 4. 附录 E 的可执行性标签

[114 项规范用例追溯索引](../fixtures/ca-sl-v1alpha3-case-traceability.yaml)新增资料性 `proposedExecutionClass` 和 `executionPlanStatus: NOT_IMPLEMENTED`，用以区分静态链接 Fixture 候选、Runtime 模拟候选、跨阶段测试、内部图分析单测、Owner 集成评审和业务评审。分类只表示建议的实施方式，不改变附录 E 的输入或规范性预期。

任何“需真实 Owner”场景仍须满足 §45.2 第 1、2、6 项的真实发布和端到端验证；`OWNER_INTEGRATION_REVIEW` **不表示已经验证了真实 Owner**。不能将 `规范用例已定义` 误读为测试脚本可运行或 CI 已通过。

## 5. 路径解析与文档闭合

G.1 明确了 `LocalSchemaPath` / `LocalScriptPath` 从右侧剥离固定后缀 `.schema.yaml` / `.py` 后再逐段验证的解析方式。此项复述已有 G.1 文法，不增加文件名合法集合，也不允许符号链接越界或路径穿越。

附录 H 的“SCHEMA_MISSING / INVALID”文字改为“两个现有代码的并列简写”，而非引入不受支持的别名；E01–E114 不变，E115/E116 不新增。现行字段身份、Schema、Effect、Capability、证据时效和完整责任模型仍以规范正文为准。

## 6. 尚未完成的符合性事项

本次修改并未生成或执行 114 个 E 用例的机器 Fixture，没有实施 Runtime/Owner 回包证明验证，也未完成 Native、WASM、Studio 或真实 5GC 的符合性测试。源码一致性与 Source Hygiene 通过后，仅可判定文档勘误通过。§45.2 的八项独立门槛继续保持 NOT QUALIFIED。

如有后续工具证明本轮表述与原有冻结行为存在实质差异，应停止以 v1alpha3 勘误名义传播该差异，并提交独立的版本化语义评审。
