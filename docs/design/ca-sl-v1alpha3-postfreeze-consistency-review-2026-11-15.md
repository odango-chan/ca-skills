# CA-SL v1alpha3 — 冻结后诊断/术语/互操作权威性复核（2026-11-15）

**分类：** §45.1 A（已修复项核对、术语及交叉索引）/ B（复述已有 Owner / Script / Evidence 规则为字段权威表和验收清单；无新的允许输入、诊断、授权来源或结果）  
**语言目标：** `connectionagent.io/v1alpha3`（vNext 仅资料性别名）  
**Normative 唯一来源：** [完整中文规范](../skill-language-spec.zh-CN.md)  
**产品符合性：** NOT QUALIFIED；本文件及 GitHub Source Hygiene 不是 §45.2 的执行证据

## P0 逐条复核

| 评审项 | 最新 `main` 基线的实际内容 | 决定 |
|---|---|---|
| H 中重复的 `EFFECT_MISMATCH` | H 已定义诊断完整身份为 `(Code, Phase)`；C_STATIC 与 R_RUNTIME 是两个不同阶段事件，日志必须保存 `code/phase/类别` | 不新增 `_COMPILER/_RUNTIME` 别名，避免破坏已冻结诊断码 |
| H 中 `LANGUAGE_TARGET_UNSUPPORTED` 错误引用 E01 | 已是“待补独立 Fixture”，E01 仍为正常链接正例 | 不重复修；未执行的 Fixture 按已存在的诊断缺口文件追踪 |
| E115/E116 未定义 | 当前完整规范没有这些正式编号，E01–E114 为冻结集合；`UNSUPPORTED_WAIT/UNSUPPORTED_V02_SYNTAX` 为既有诊断，另待可执行 Fixture | 不增加虚构 E 编号 |
| 第八部分缺失 | 完整规范有 `# 第八部分：Script 与开发工具链`，第七、第八、第九部分连续 | 不更动章节标题 |
| `dependencyId` / Contract Alias | §34.0 已强制 `snapshot.dependencyId == alias`，Package ID 须与 `Contract.dependencies[alias]` 严格相同 | 只统一名称：Dependency Alias、Workspace Dependency ID、Stable Package ID；无新映射 |
| Host Context / Invocation Context | §11.5、G.6 已分别校验 Host Schema 和 Request Schema，再产生只读 `effectiveContext` | §6.3 增加一句总定义，强调 Host Context 只是 Host 部分，不是另一份 Context |

## P1 已完成的交叉索引与作者指导

1. **F.1 Mutation / Reconcile 字段权威索引。** 列出 Receipt/Proof、失败类别、Reconcile callable、恢复 Output、资源责任与 Compiler/Runtime 适用规则。原规范性判断仍由 F.1、§20 与 G.2.2 共同明确，不新增第二套不同规则。
2. **F.3 Evidence 描述符索引。** 列出 authority、fact、producers、scope/correlation、factValue、selection、freshness、sourceIdentity / IndependentDomains、factIdentity 的已有职责与错误分类。§17 / G.3.1 的精确路径/作用域规则不被表格放宽。
3. **§12.6 Result Sufficiency。** 明确 SHOULD 是业务评审与 Studio 的 Review Checklist，不单独生成“是否足够”的 Compiler 诊断；可静态判定的类型、路径、Schema、Evidence 仍由现行规则验证。
4. **§45.2 Script 最低验收清单。** 现有 §32/F.6 要求被整理为六类机器验收：入口 TypedDict、字面量键、可缺失键守卫、严格输出、受支持注解、Native/WASM/Studio 诊断一致性。版本和 CI 原始证据仍须真实填报。
5. **Owner Schema 投影、可选 SourcePath、Evidence requires、CEL 与 Reconcile UNRESOLVED** 已在 [作者指南](../guides/ca-sl-v1alpha3-authoring-patterns.md) 中补齐可操作流程，明确没有新的 Owner 发布格式或 Skill 信任来源。
6. G.2.1 的教学 Fragment 标记提前到代码之前，防止误以为一段 `spec.contracts[]` 条目可以单独当 ToolCatalog 完整文件。
7. **附录 H 高频运行诊断不重新分类。** 现有 `TOOL_UNAVAILABLE`、`EVIDENCE_STALE`、`SCOPE_MISMATCH` 已有派发前/派发后与 Mutation/READ 的精细行为；尤其已派发 READ 的回包 Scope 不匹配必须按证据不可信和 UNKNOWN/停止处理，**不能**误沿派发前 `DENIED` 继续业务。H 的 `(Code, Phase)` 与 §24.2 仍是规范性判断来源。

## 不变性与仍待完成的工作

- **没有改变**单一 DAG、四阶段、SourcePath/Schema 可接受集合、身份来源、Capability Grant、Effect、Evidence 验证、Mutation UNKNOWN、Reconcile 次数、Stop 状态和 E01–E114 的规范性预期。
- **没有宣称** Owner 身份输入的物理传输格式、跨快照专用 Reconcile 标记、Root Routing / Applicability 完整协议或真实 ToolCatalog 发布物已经版本冻结。它们应走独立协议交付和 §45.2。
- E01–E114 的资料性逐例镜像位于 [case-traceability.yaml](../fixtures/ca-sl-v1alpha3-case-traceability.yaml)；未完成的诊断候选位于 [diagnostic-fixture-gaps.yaml](../fixtures/ca-sl-v1alpha3-diagnostic-fixture-gaps.yaml)。候选记录不是可执行 Fixture，不得当成 PASS。
- 本轮仅作文字和信息架构的检查，不代表自动化验证的脚本检查器或完整机器 Fixture 已建成。Compiler、Studio、Runtime、Owner 和真实 5GC 产品状态仍是 **NOT QUALIFIED**。

若评审发现上述任一澄清实际改变既有合法输入集合、诊断或安全结果，应停止按 §45.1 A/B 合入该项，改按 C 类另行升级互操作或语言版本。
