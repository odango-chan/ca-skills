# CA-SL v1alpha3 互操作与实现基准澄清记录

**分类：** 冻结后 A 类文字/索引勘误、B 类现有规则的适用范围澄清  
**版本：** CA-SL vNext / API v1alpha3（FROZEN）  
**实现符合性：** NOT QUALIFIED  
**规范依据：** [CA-SL 完整规范](../skill-language-spec.zh-CN.md)  
**相关历史：** [诊断追溯与 PSI 身份来源勘误](ca-sl-v1alpha3-diagnostic-trace-errata.md)

## 1. 本轮 P0 复核裁决

| 评审事项 | 已验证的现行状态 | 裁决 |
|---|---|---|
| 附录 H 的 E115/E116 悬空引用 | 在当前 `main` 中均不存在；§45.2 的正式用例范围为 E01–E114 | 不新增 E115/E116；既有缺口由 DFX 资料性登记跟踪 |
| `LANGUAGE_TARGET_UNSUPPORTED→E01` | 已改为 `待补独立 Fixture` | 无需重复修改或冒充用例通过 |
| 同名 `EFFECT_MISMATCH` | 附录 H 以 `(Code, Phase)` 唯一分类；C_STATIC 与 R_RUNTIME 是不同事件 | 保留规范性键；符合性报告应同时记录 `code`、`phase` 与当前严重性/类别 |
| G.4 未点名 `$defs`、`definitions` | 已有许可关键字白名单中不包含，未知关键字统一 `SCHEMA_INVALID` | 直接补充明确排除及 `#/$defs/...` / `#/definitions/...` 片段引用不受支持；不改变允许的 Schema 集合 |
| CEL/Python 具体解释器与工具版本 | G.4、F.6 冻结允许的表达式/类型，§45.2 仍要求跨产品一致性；未冻结外部库版本 | 区分语言支持剖面与实施版本，符合性报告记录实际解释器/检查器版本；**不在 v1alpha3 勘误中新增硬性运行版本** |

结论：前三项属于已经解决但未被本轮评审所引用的既有勘误；G.4 中的 `$defs` 禁止规则可由现有白名单直接推出；CEL/Python 的具体工具版本不能仅通过一次规范编辑确定为已冻结语言要求。

## 2. CEL 与 Python 的可复现实测基准

CA-SL 的规范性输入集合由 G.4、F.6、§32 定义，不由具体第三方解析器的默认配置决定。为了执行 §45.2 第 3–5、8 项，实现符合性报告应提供以下实际环境标识与原始结果：

| 组成 | 可重复性记录 | 尚未验收的事项 |
|---|---|---|
| CEL parser、type checker、evaluator | 实际实现名称、软件版本或不可变源码提交、启用的函数/宏/常量清单 | G.4 白名单外语法的拒绝、has/size/可空守卫、int64/binary64、UNKNOWN 处理 |
| Python AST/typing 分析器 | 前端名称、版本/源码提交、支持的语法模式、注解处理策略 | TypedDict 继承、Required/NotRequired、`from __future__ import annotations`、可解析/不可解析前向引用、Annotated 约束映射 |
| Script Runtime / Sandbox | Python 实际执行环境版本、沙箱实施、资源预算与超时参数 | 纯函数约束、输出 Schema 校验、错误与异常归类 |
| JSON Schema 解析与链接 | 解析器版本/源码提交、所用 Draft 2020-12 子集校验配置 | 精确 `$id`、无循环的受信引用闭包、禁止 `$defs` 和未知关键字 |
| Native/WASM/Studio 入口 | 每个构建产物和源码提交、同一输入字节快照、原始诊断/执行记录 | 逐输入完全一致，不以单平台 PASS 代替互操作通过 |

官方 Python 3.11 标准库为 `typing.Required` / `typing.NotRequired` 提供了直接支持。**Python 3.11 可以作为实现验证的候选基线，但并非本次 v1alpha3 勘误新增的强制运行版本。** 同理，CEL 引擎即使支持额外的宏或算术，也不得向 CA-SL 语言开放 G.4 以外的操作。

## 3. 升版候选（不属于本次勘误）

以下事项的不同选择可能改变可接受源码、类型派生或可观测错误分类，须经 §45.1 C 类版本化设计评审，而不能作为 v1alpha3 的静默补丁：

- **Schema 扩展：** 是否允许 `$defs`/JSON Pointer 片段引用；若允许，如何按信任快照解析本地与跨 Schema 引用、拒绝递归、绑定独立 `$id`。
- **CEL 基准固定：** 选择稳定 CEL 语法/规范标识与参考解释器提交、函数注册及宏策略，并证明与当前 G.4 有限表达式集合一致；若其附带新的合法/非法形式，需升版。
- **Python Script 语法：** 是否把 Python 3.11 作为强制最低解释器版本；如何定义继承、total、forward-reference、Annotated 元数据来源及受支持语法错误映射。
- **Owner 投影等价性认证：** 若需新增机器可验证的原 Schema/投影等价性承诺、源版本或签署结构，应由正式 Owner/互操作契约定义并发布。
- **条款级稳定 ID：** 新增 `§17.2.4` 等细分规范性条款编号须保持既有交叉引用，必要时作为独立规范版本整理。
- **跨章节合并权威决策表：** 现行 §20.1、§20.3、G.2.2 均已有规范性定义。若要将其替换成一个新的唯一表，应作为明确的文本结构/规范性归属修订单独评审，避免移植时遗漏证明规则。

## 4. 本轮交付物

- G.4 明确 `$defs`、`definitions` 与 JSON Pointer 片段引用不在 v1alpha3 白名单中。
- F.6/F.7 明确语言剖面与解析器/执行器版本的区别。
- [Mutation、Reconcile、Evidence 决策与条款索引](ca-sl-v1alpha3-decision-and-trace-index.md)为资料性导航，不取代规范性决策表。
- [SourcePath、Evidence、Owner 投影作者指南](../guides/ca-sl-v1alpha3-authoring-patterns.md)为资料性实施建议。
- 附录 B/D 明确标记为历史记录，现行八项符合性门槛仍为 §45.2。
- 诊断的唯一规范性名称索引仍为附录 H；[E01–E114 预期索引](../fixtures/ca-sl-v1alpha3-case-traceability.yaml)与[39 项诊断缺口清单](../fixtures/ca-sl-v1alpha3-diagnostic-fixture-gaps.yaml)继续独立追踪。

## 5. 发布裁决

这是一份 **v1alpha3 冻结后勘误与澄清**，不重新冻结语言、不修改 E01–E114 的预期、不替代 §45.2 任何 Owner/Compiler/Studio/Runtime/5GC 的实测符合性。

如需将升版候选纳入实际语言规则，应先形成独立规范性提案，选择新的语言或互操作版本，并提供完整正负例与安全迁移解释。对于尚不存在可执行 Fixture 的诊断，不得标记为已通过。
