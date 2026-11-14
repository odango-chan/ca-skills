# CA-SL v1alpha3 — 摘录评审复核与冻结范围勘误（2026-11-15）

**分类：** §45.1 A（文档排版、展示版本、目录说明）和 B（已有 §12.8 Root Routing 外部归属的冻结范围澄清、§17.1 来源豁免正负例）  
**权威 Normative 源：** [CA-SL v1alpha3 中文规范](../skill-language-spec.zh-CN.md)  
**产品状态：** NOT QUALIFIED；本勘误不构成 Compiler、Studio、Runtime、Owner 或真实 5GC 的可执行验收。

## 完整规范与片段评审的差异

| 片段评审意见 | 当前完整规范事实 | 裁决及本轮动作 |
|---|---|---|
| P0-1 附录 F/G/H、§30–§45、关键 E 用例似乎缺失 | 所有相关章节及 E.3/E.6/E.8/E46/E60 均在一个受版本控制的 `docs/skill-language-spec.zh-CN.md` 文件中。第十一部分 §46–§91 是资料性解释，不存在单独的规范性 FAQ 附件 | 非当前文件缺失；在 §0 明确同一文件组成和规范效力 |
| P0-2 §29 CEL 使用未声明 `expected` | 两处现有 CEL 均写 `ranSetup.currentSessionInstanceRef == expectedSessionInstanceRef`，参数同名、完整表达式有闭合结尾 | 摘录截断造成误判，不修改完整规范的正确 CEL |
| P0-3 5GC 请求 PSI/DNN/S-NSSAI 充当身份 | §13.3、§28、§30、§31 已明确仅可作为请求业务选择值；任何 Owner/部署标记为身份/Scope 输入时不得直接取 request，必须来自受信 Host 投影或权威 Producer | 不增加隐式 request 身份豁免、不虚构 Host 内建字段；真实 Host/Owner 的可信 PSI 绑定尚待产品验收 |
| P0-4 Applicability/Root Routing 未冻结 | §12.8 已把 Skill Eligibility 归 Host/Root Routing 并要求无法唯一匹配时拒绝准入；但完整选择算法与 Applicability YAML 未定义在 v1alpha3 作者语法 | **实际展示边界不够醒目**。§0 新增冻结/未冻结分界，§12.8 重申不接受未发布的 Applicability 字段或隐式默认策略 |
| P1-1 “省略参数”措辞 | §17.1 已专门强调省略的是 `evidence.requires[parameter]`，不能省略参数和实参 | 添两个资料性调用点对照例，不改变 E 用例预期或 Evidence 判定 |
| P1-2 Normative / Informative 教学混合 | 文本已区分附录 E 的预期（Normative）与教学数据（Informative），§22.1/H 的规范权威已补清 | 在 §0 增加统一效力索引；不降级附录 H 的规范性诊断分类 |
| P1-3 去掉 `vNext` | §0 原本已定义它是资料性别名，机器目标精确值为 `connectionagent.io/v1alpha3` | 首页显示机器目标；`vNext` 可保留在历史/迁移说明中，不当作新机器版本 |

## A/B 不变性检查

- 没有添加或删除 SourcePath 根、YAML 作者字段、Predicate 参数类型、Capability、Owner Outcome、路由键、诊断代码或 Runtime 终态。
- §29 的 `expectedSessionInstanceRef` 原本已正确，本次没有修改表达式或扩大 CEL 语法。
- 没有定义新的 `context.session.*` 作为 v1alpha3 内置 Host Schema，也不允许把 Request 数据直接视为 Scope 身份。
- 已有 §12.8 非唯一 Skill 拒绝规则保留；仅说明 Root Routing 完整语法属于外部版本化契约，不是本版遗漏但可猜测的默认语法。
- `evidence.requires` 的豁免正反例严格继承 §17.1 对所有调用点的现有约束。
- 纠正 §0 的 Markdown 表格跨行排版错误，不改变表中规范性结论。
- 当前附录 E01–E114 与 H 的 `(Code, Phase)` 规范性身份保持不变。

## 仍待独立交付

1. 独立 Root Routing / Skill Eligibility 互操作语法及其选择优先级、歧义拒绝机器 Fixture；本文件只冻结 fail-closed 原则。
2. 受信 Host/Owner 的 Session/PSI 来源投影以及 §13.3 的 Owner 身份输入发布格式，不得借示例推断已存在。
3. §45.2 的 Compiler Native/WASM/Studio、Runtime/Host、Owner 导出与 5GC 36 Case 的真实执行及 CI 记录。

**冻结裁决不变：CA-SL v1alpha3 核心语言语义 FROZEN；外部 Root Routing 完整协议未冻结于本版；产品符合性 NOT QUALIFIED。** 若后续需求要求增加 Applicability 作者语法或身份授权豁免，按 §45.1 C 类另行升级相应语言或互操作版本。
