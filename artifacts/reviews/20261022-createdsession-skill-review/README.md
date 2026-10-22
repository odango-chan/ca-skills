# CreatedSession Skill 语义评审

结论：**CHANGES_REQUIRED；保留 Draft，不合入或作为组件实现基线。** 当前有 3 项 P1 阻断和 4 项 P2 问题。原先 package/schema/图检查的 PASS 仍成立，但不能推出可编译、用例预期正确或业务证明充分。

本次评审对象固定为 [ca-skills d3576dc](https://github.com/odango-chan/ca-skills/tree/d3576dcdd0dce732cb284da28d8105976e63d6a0/skills/establish-pdu-session)，不是后续报告提交后的新业务版本。语言/编译器参考 ca-skill-toolchain `07a8ee41ca456265e116812ff0ad31fe74333451`，Runtime 参考 `9db2230c172da8742ecfc5049cbfbd1a71b7828f`。追踪：[ca-skills#20](https://github.com/odango-chan/ca-skills/issues/20)、[Draft PR#21](https://github.com/odango-chan/ca-skills/pull/21)。本次交付评审与反例，业务源码尚未修复。

## 1. P1：两个 facts 输入绑定无法按 Case 的实际值解析

位置：[procedure.yaml L19](https://github.com/odango-chan/ca-skills/blob/d3576dcdd0dce732cb284da28d8105976e63d6a0/skills/establish-pdu-session/assurance/procedure.yaml#L19)，以及 predicates.yaml 中全部 `facts.createdsession_ingress.value.ref` scope。

Procedure 使用 `context.facts.createdsession_ingress.value.ref`、`context.facts.createdsession_lifecycle.value.ref`。Case 的 `value` 是 PlanningContext 序列化包装；当前 Mock Runtime 的 [resolveContextPath](https://github.com/odango-chan/ca-skill-toolchain/blob/07a8ee41ca456265e116812ff0ad31fe74333451/backend/internal/mockruntime/runtime.go#L315) 先将 `Fact.Value` 投影为 facts 根，然后再遍历路径。以真实 Case 为输入，根值已是 `{ref: synthetic-ingress-a}`，继续取 `.value.ref` 失败。

实际反例中两个路径均无法解析；删掉包装层后能在 Mock 的值空间取到 ref。即使所有未知 Capability 已发布，正向 Case 到 `inspect-policy-context` 的 ingress/lifecycle 输入仍会遇到绑定问题。这里是按源码路径算法得到的结论，未执行 Go Mock Runtime。

生产 Runtime 还不能靠“删掉 `.value`”直接宣称闭合：[resolveProcedureInputBinding / BindingFact](https://github.com/odango-chan/ca-runtime/blob/9db2230c172da8742ecfc5049cbfbd1a71b7828f/internal/execution/engine/procedure_template.go#L375) 按完整 FACT path 查键，并不自动遍历同样的外层包装。需要明确真实可信 context 的键/值与冻结输入绑定，核验 Predicate CEL 的 facts 形态。不得在 fixture 再套一层 value 来迎合错误路径。

修正完成条件：一个真实 admitted ingress/lifecycle 输入在 source→Artifact→Runtime binding 和 Case 中均能解析；缺失/类型错误保持 fail closed；无额外的模型授权标记或私有注入规则。

## 2. P1：UDM Predicate scope 与现有候选 Catalog 不兼容

位置：[predicates.yaml L130](https://github.com/odango-chan/ca-skills/blob/d3576dcdd0dce732cb284da28d8105976e63d6a0/skills/establish-pdu-session/assurance/predicates.yaml#L130)。

Skill 查询 `sbi.operation.result` 时提交 `{ueRef, pduSessionId, ingressRef}`，而其声称复用的 [Runtime A Catalog](https://github.com/odango-chan/ca-runtime/blob/9db2230c172da8742ecfc5049cbfbd1a71b7828f/contracts/proposed/createdsession-udm-get/v0.1/observation-catalog.example.yaml#L5) 要求 `{ueRef, invocationId, transactionRef}` 且禁止额外字段。把当前 scope 形状直接交给该 schema，得到 3 项错误：缺 invocationId、缺 transactionRef，以及多出 pduSessionId/ingressRef。

这不是只缺 active 注册。Predicate 也没有将实际 `get-sm-data.output.transactionRef/requestRef/fabricRecordRef/digest` 接到 acquisition，当前文档所说“精确锁定当前 Get 并与 ToolResult 同源”尚未落实到机器绑定。同一 ingress 内多次调用、旧调用或其他操作不能靠 UE/PSI/时间接近区分。

修正完成条件：通过现有 verify subject projection / 获准绑定能力把真实调用身份接入 scope；不得从模型获取可信 invocation 或 transaction。使用目标 Catalog 实际校验，并覆盖错误 invocation/transaction/record/digest、历史结果、超时与迟到材料。若既有绑定机制不足，先向 Runtime/Toolchain 提供最小证明，不扩展 Skill 私有语法。Runtime owner 仍为 [#172](https://github.com/odango-chan/ca-runtime/issues/172)。

## 3. P1：只读不确定结果的分支无法按当前 Artifact 规则冻结

位置：[procedure.yaml L39–54](https://github.com/odango-chan/ca-skills/blob/d3576dcdd0dce732cb284da28d8105976e63d6a0/skills/establish-pdu-session/assurance/procedure.yaml#L39)。

`get-sm-data` 是 read_only，`OUTCOME_UNKNOWN` 却直接去 terminal `UNRESOLVED`。当前 [proceduretemplate/compiler.go 的 analyzeGraph](https://github.com/odango-chan/ca-skill-toolchain/blob/07a8ee41ca456265e116812ff0ad31fe74333451/backend/internal/proceduretemplate/compiler.go#L284) 对任何普通 Action 的这条边都要求“受支持的 recovery orbit 或 SAFE_STOPPED”，该检查发生在 ToolResolver/effect 解析之前。因此这里有独立于新 Registry 依赖的 Artifact 结构冲突。

还存在 owner 契约不一致：Toolchain Capability schema 的 read_only outcomes 允许 UNKNOWN、不允许 OUTCOME_UNKNOWN；Runtime 的 UDM Get 候选却声明 OUTCOME_UNKNOWN，实际 Action Kernel 对部分 transport/remote uncertainty 也导出该结果。不能把只读请求改成 mutation 或发明 pending write 来绕过它；也不能只改 Skill 分支名字就声称跨仓一致。

已单独归位到 [ca-skill-toolchain#131](https://github.com/odango-chan/ca-skill-toolchain/issues/131)，与 Runtime#172 联合冻结真实只读不确定结果、终态/继续行为和 pending-write 含义。此结论是 source/contract 审查，不是已运行 compiler 的报错记录。

修正完成条件：使用真正 owner Capability/Artifact 完成 focused build 与 Runtime 不确定结果执行；证明既不伪造 NF 变更知识，也不削弱 mutation 的恢复/重试约束。HTTP/MCP caller wait 与执行期限仍分别处理。

## 4. P2：15 个 Case 的 postcondition actual 与已写分支矛盾

位置：`cases/06…16`、`19`、`21`、`22`、`24`，详见 [counterexamples.json](counterexamples.json) 的 fixtureWalk。

这些 Case 普遍把失败/未决路径的全部 actual 写成 NOT_EVALUATED，但对应 Predicate 已经执行。例如 Case12 的 RAN Predicate fixture 为 FAIL，随后 handoff-unresolved 的资源管理 Predicate 为 PASS，两个都不是 NOT_EVALUATED。Case16 已验证 RAN/N4/UE 为 PASS，资源管理为 UNKNOWN，四个结果同样不应全写未执行。

本次仅按作者写下的分支/fixture 推演，假定数据绑定已成功；未执行实际 Tool、Predicate、pending-write 或 Go Mock Runtime。真实 runner 可能先被前述问题阻断，不能将这 15 个源预期矛盾描述为“已经跑了 15 个 Mock 失败”。当前 owner [computePostconditions](https://github.com/odango-chan/ca-skill-toolchain/blob/07a8ee41ca456265e116812ff0ad31fe74333451/backend/internal/mockruntime/verify.go#L22) 保留已执行 Predicate 的实际结果，不能以最终不是成功为由清空它们。

Case 也尚未挑战三种 handoff mutation 的未知结果、预算在创建后耗尽等关键路径；所有 handoff fixture 都直接给 COMMITTED。数量不是覆盖充分性的依据。

修正完成条件：按真正访问过的 Predicate 保留 PASS/FAIL/UNKNOWN，未访问才是 NOT_EVALUATED；补足有责任残留的 handoff/预算/恢复义务；实际执行 owner Case gate 并保存结果。不能用手写 fixture walkthrough 替代资格。

## 5. P2：UDM 已选配置到 PCF 的可追溯数据流不完整

位置：[select_establishment_configuration.py L30](https://github.com/odango-chan/ca-skills/blob/d3576dcdd0dce732cb284da28d8105976e63d6a0/skills/establish-pdu-session/scripts/select_establishment_configuration.py#L30)、[procedure.yaml L61–146](https://github.com/odango-chan/ca-skills/blob/d3576dcdd0dce732cb284da28d8105976e63d6a0/skills/establish-pdu-session/assurance/procedure.yaml#L61)。

选择脚本读入完整 subscription，却只返回 DNN/slice/type/SSC。其后的 policy context 和 PCF Create 没有传递 Get 的 data/ref；Create 的 `subscriptionRef` 来源是 SDM Subscribe 的资源引用，不能当作 UDM SM subscription data。真实向量含 sessionAmbr/defaultQos 时，脚本输出会丢掉它们。

如果当前 PCF profile 要使用这些配置，adapter 将无法仅按显式输入追溯它们；如果有意不用，应在正式 profile 中明确说明及证明来源替代。不能从临时 SMF 缓存或未声明的再次 Get 中默默补齐，更不能把接口标准可选与目标 profile 不需要混为一谈。

修正完成条件：逐字段决定保留/不使用；需要的已选数据或精确受限 ref 沿生产节点显式传给消费者。用两份仅 AMBR/QoS 不同的合法 UDM 结果证明目标请求按预定规则变化，并保持 DNN/slice/type/SSC 与同一数据来源一致。具体 profile owner 为 Provider#19。

## 6. P2：局部 Tool 输入 schema 太宽，允许实现误接受或崩溃

位置：`schemas/selection-input.schema.yaml`、`schemas/protocol-response-evaluation-input.schema.yaml` 及三个 scripts。

实际调用当前脚本得到四个反例，均能通过它们自己声明的局部输入 schema：

| 输入 | 实际结果 |
| --- | --- |
| allowedSessionTypes 为含 IPV4 的字符串 | Python 子串判断使选择成功 |
| allowedSscModes 为 `[true]` | Python 的 `1 == True` 使选择成功 |
| UDM HTTP200/MATCHED，但 subscription 为 null | evaluate-udm-read 返回 PASS |
| AMF response 的 httpStatus 为 null | evaluate-transfer-start 抛 TypeError |

这些反例**不代表**已经穿过正式 admitted Observation：正确的强 A result schema / Evidence Gate 可先拒绝非法数据。问题是当前本地 Tool schema 和实现的独立边界并未表达这个前提；两个响应脚本共用一个只约束 response 为 object 的输入 schema，也不足以证明各自协议字段类型。

修正完成条件：复用正式源 schema 或建立明确的强 typed adapter 输入；对必需字段、枚举、整数/布尔、对象/null、列表、错误数据和证据 metadata 给出一致策略。不可用“捕获所有异常并返回 FAIL”把基础设施错误伪装为业务反证，也不能只补同一实现的自证用例。

## 7. P2：调和的 source/Capability/冻结执行含义不一致

位置：[procedure.yaml L117](https://github.com/odango-chan/ca-skills/blob/d3576dcdd0dce732cb284da28d8105976e63d6a0/skills/establish-pdu-session/assurance/procedure.yaml#L117) 等六个节点，及 source-candidate 文档中 `createdsession.operation.reconcile / read_only` 的依赖行。

不能把 Runtime 的恢复简单写成一个新 read_only Capability，并要求它返回 COMMITTED/NOT_COMMITTED/UNRESOLVED：这三个值不是现行 Toolchain read_only Capability 允许的结果。语言已有专用 `reconcile`/恢复 lineage；应由可信 Runtime Reconciler 消费原 invocation 知识。

需要保留一个细节，避免误报：当前 [proceduretemplate/compiler.go 的 isReconcileNode/analyzeRecoveryOrbits](https://github.com/odango-chan/ca-skill-toolchain/blob/07a8ee41ca456265e116812ff0ad31fe74333451/backend/internal/proceduretemplate/compiler.go#L623) 会按结果结构识别旧式 recovery，并将这些节点折叠到 ExecutableRecovery。因此**不能断言**当前六个 call 一定冻结成普通网络调用，或 Runtime 一定无法调和。但这恰好说明文档所说“再调用一次新 Tool”不等于冻结后的执行语义，不能以此安排新的 Runtime API 开发。

修正完成条件：对齐现有恢复建模，移除不必要/不合法的新 Capability 依赖，核验 source→Artifact 的原 mutation lineage、pending-write、可信调和次数和 retry=false 行为。不能只把关键字机械替换后跳过实际 Artifact gate；兼容 lowering 与 canonical source 均需 owner 核验。当前 conservative stop 可以保留，无需为了可恢复输出而扩大首期流程。

## 8. 三项执行契约依赖仍需冻结

这些是当前已公开的未完成依赖，不把“尚未实现”本身重复计作源码 bug；但它们必须在作为可执行基线前闭合。

1. **来源与比较基线。** 最终 Predicate 当前只检查 requiredFlowMatched/downlinkTunnelMatched/selectedConfigurationMatched 等布尔值。必须给出原生字段、实际 NAS/N2 artifact/预期 flow/config、当前实例及 transfer 的精确 join；source 不应自行拥有不透明的 Skill verdict。仅供 UE/PSI/ingress 的 scope 和“CURRENT”标签不能完成这些证明。优先用充分的 typed 事实与明确比较；若采用派生事实，须正式冻结其输入/算法/证据与 Runtime 权威边界。
2. **首次创建之前的持续责任。** requiredFacts 中有 lifecycle ref、policy context 有 callbackReady，不等于已经证明持久操作登记、receiver readiness 与迟到/未知资源责任。需明确可信准入/adapter 在发送前的保证，且覆盖预算耗尽、取消、崩溃、调和未决；不能等最后 handoff 才第一次保存责任。
3. **真实资源与唯一发送。** 地址、uplink endpoint、flow、策略与当前实例来源，以及原 SMF transfer 与 Agent transfer 的精确单次发送/失效规则仍未实现。Provider 计算器只解决 bytes，不解决这些前提；不能只把 uniqueSenderReserved 布尔快照当作发送时的原子授权。

本轮没有理由改变“Agent 决定 N1/N2 SM 业务、Provider 计算、SBI 独立发送、Fabric 留证、Runtime 裁决、AMF 外层安全/NGAP、临时 SMF N4”的职责。IPv4/SSC1/单默认 non-GBR 的首片范围也无需扩大。现有设计中 AMF ACK 不等于完成、RAN/N4/UE 分别证明、unknown 不盲重试的方向应保留。

## 9. 实际验证与修正顺序

| 检查 | 本次结果与实际边界 |
| --- | --- |
| package/layout、30 owner-schema、5 local schema meta-check | PASS；只证明相应结构 |
| 38 节点 reachability / 24 producer binding dominance | PASS；不是字段覆盖、事实解析或恢复语义证明 |
| 原有 20 个纯计算向量 | PASS；没有覆盖本次四个坏输入反例 |
| 新反例 | 实际 JSON Schema 校验、脚本调用与只按分支的 fixture 推演；[counterexamples.json](counterexamples.json) |
| focused compile / make verify | 再次尝试；ENVIRONMENT_BLOCKED，退出 1/2；[owner-gates.json](owner-gates.json)、[focused log](focused-compile.txt)、[full log](make-verify.txt) |
| actual compiler / Artifact build / Go Mock Runtime | 未运行到；新增 Registry 依赖也未闭合，不能声称 compiler FAIL/PASS |
| CEL / owner Predicate、SQ、NAS/NGAP codec、协议/实网 | NOT_RUN |

修正先后：① 对齐 facts 与精确 transaction 绑定；② 与 Toolchain#131/Runtime#172 冻结只读 uncertainty，并核验原生 mutation recovery；③ 闭合所选配置与后置条件的数据/证据流；④ 修正 Cases、强化局部 schema，补关键义务；⑤ 用真实契约执行 source→Artifact→Runtime/资格，再按 A→B→C 开发与实网验收。

没有实际 owner gate 之前，不合并该 Skill，不生成 qualified Artifact，不让组件实现把未闭合名字当作已批准机器契约。
