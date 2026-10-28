# CreatedSession Skill 源码候选与依赖反查

状态：Proposed v0.1；owner：[ca-skills#20](https://github.com/odango-chan/ca-skills/issues/20)。

语义评审：**CHANGES_REQUIRED**；[完整评审](../artifacts/reviews/20261022-createdsession-skill-review/README.md)发现 3 项 P1 和 4 项 P2，包括 facts 绑定、精确 UDM 取证 scope、只读不确定结果的 Artifact 契约，以及用例预期/数据流/局部类型/调和建模。静态 PASS 不代表可执行；修正和 owner gate 前保留 Draft。

`skills/establish-pdu-session/` 是覆盖完整初始建立目标的源码候选，尚未通过引用闭合、编译、资格或生产准入。它不是单条 UDM Get 的包装 Skill，不使用模拟器的 pdu_session.create/ensure，也不依赖 canonical establishment/absence 布尔值。

设计输入为 Sandbox [总设计](https://github.com/odango-chan/sandbox/blob/460c4628eb54a97de2485e1b41ed76db9ba22d23/docs/design/createdsession-agent-orchestration.md)、[输入](https://github.com/odango-chan/sandbox/blob/460c4628eb54a97de2485e1b41ed76db9ba22d23/docs/design/createdsession-procedure-context.md)、[B](https://github.com/odango-chan/sandbox/blob/460c4628eb54a97de2485e1b41ed76db9ba22d23/docs/design/createdsession-resource-lifecycle.md)、[C](https://github.com/odango-chan/sandbox/blob/460c4628eb54a97de2485e1b41ed76db9ba22d23/docs/design/createdsession-n1n2-verification.md)。源码采用 Toolchain `07a8ee41` 的现行 schema，不修改语法或 active Registry。

## 1. 支持范围与输入

首个候选仅处理本地非漫游、3GPP、明确解码为 IPv4/SSC 1、单默认 non-GBR flow 的初始请求。请求中缺失提取的类型/SSC 不用订阅默认值代填；其他模式留给后续 profile。`request` schema 是本 Skill 的语义输入，不是 NetworkIntent v2 的扩展。输入如何从精确 ingress 提取/准入仍归 Sandbox#30/#32、Fabric#70 和 Runtime#172。

| 输入 | 来源与约束 |
| --- | --- |
| subject.ueRef | 已准入 subject binding；不是模型剥离前缀得到的 SUPI |
| request.pduSessionId/dnn/sNssai/servingPlmn | 精确初始请求的规范化语义；DNN 精确匹配，MNC 保留宽度，SD 缺失与零分开 |
| request.requestedPduSessionType/requestedSscMode | 精确 N1 typed decode，首片只允许 IPV4/1；不是给冻结 v2 新增字段 |
| facts.createdsession_ingress.value.ref | Host/Runtime 注入的当前初始事件绑定；普通字符串、facts.authoritative 或 Case fixture 本身不授予真实权限 |
| facts.createdsession_lifecycle.value.ref | 创建前已获准的持久资源/通知责任 scope；相关服务必须已经存在且可恢复，不由只读查询临时创建 |

produced subscription、policy、context、response artifact 与 operation ref 都从生产节点输出传递，不伪装成预先存在的 context.facts。Protocol refs、部署绑定、地址与 bytes 不写进模型 SKILL.md。

## 2. 完整流程与有意收窄的恢复

流程覆盖：入口核验 → UDM Get/结果判断 → 确定性选择 → PCF/订阅 context 核验 → SDM Subscribe → PCF Create → 初始 N4 核验 → Provider 协议工具计算 NAS/N2 响应产物 → 单次 AMF transfer → 等待/独立核验 RAN、N4、UE → 资源责任移交和最终后置条件。

选定工具 owner 为 ca-provider-5gc：一次 local-compute response.prepare 按已准入的真实 context/选择/策略构造 NAS 与 N2 SM，返回不可由模型修改的 responseArtifactRef；后续另一次 Namf N1N2MessageTransfer 才发送网络请求。Provider 纯计算核心不选择 DNN/SSC/QoS、不分配地址或 N4 资源、不读取/发送网络、不写 SMF 状态；可信 adapter 在调用前物化获准输入。Fabric#70 继续负责精确源记录、介入和实际网络事实；AMF 保留 NAS 安全与外层 NGAP/N2/SCTP。完整 codec/Tool 尚未实现，不能由 Fabric 的 opaque/minimal-header 能力推导它已经存在。工具 owner-local 设计见 [消息工具](https://github.com/odango-chan/ca-provider-5gc/blob/d4ddd94d89aa7f95c771da6350f71fad60bb9cfb/docs/design/createdsession-message-tools.md)。

SMF ACTIVATING 取得 N2 的两次 SBI 方案保留为备选，需要不同显式 Procedure，不能塞进 local_compute Tool 或依靠 ProviderBinding 把 effect 偷换为 mutation。本源码候选不包含该备选图，不把它设为主流程依赖。

创建/transfer 出现 OUTCOME_UNKNOWN 时只调和一次；仍未决则停止，不触发另一次变更。调和为 COMMITTED 也不读取原失败节点可能缺失的 Location/产物，而是移交并保守停止，后续恢复须有新准入。NOT_COMMITTED 同样不在本次调用内重试。此选择避免跨分支隐含 output 合并，也避免为当前业务修改语言。

资源管理采用 B 允许的持续管理者确认路径。responsibility.transfer 只转交持久记录/责任，不偷偷执行多条 UDM/PCF 删除。管理者必须在任何创建前就接收操作身份、callback 与已知/未知资源责任；因此 pending write 未解决时可以直接安全停止，不需要另发一个会被 pending-write gate 阻断的 mutation 才“留下记录”。现阶段不宣称删除或释放远端 session。

## 3. Capability 逐项反查

除 A 已有机器候选外，下表新增名称是**本次 authoring 的暂定依赖引用**，供 owner 审查输入/输出和 outcome；不是已发布 CapabilityContract、Tool、API 或 active 注册。对应 owner 必须正式发布或替换它们后才可建立 Artifact。不得伪造 Registry/ProviderBinding 使编译看似通过。

| 引用 / effect | 本候选要求的输入 → 输出 / 结果 | Owner 与 blocker |
| --- | --- | --- |
| sbi.udm.sm_data.get / read_only | 精确 ueRef/DNN/slice/PLMN → 已发布候选 result；真实 HTTP 失败也是结果 | Runtime 9db2230、Provider#18、Fabric#70；候选尚未 active 注册 |
| fivegc.session.operation_context.read / read_only | ingress/UE/PSI、selection、lifecycle、purpose → contextRef | Provider#17 只读 source；Runtime#172 准入；无 allocator、无 N2 codec；context 存在不自动证明当前实例 |
| sbi.udm.sdm_subscription.create / mutation | contextRef/lifecycleRef → subscriptionRef、operationRef | Provider#19；精确 consumer/callback、创建前持久责任、Location 归属待发布 |
| sbi.pcf.sm_policy.create / mutation | context、选择、subscriptionRef、lifecycle → policyResultRef/operationRef | Provider#19；PCF 实际地址要求和同 SUPI/PSI 复用/改 callback 仍需隔离证明 |
| fivegc.session.establishment_response.prepare / local_compute | 当前 context、选择、policyResultRef → responseArtifactRef，封装精确 NAS/N2 产物及版本/digests | [Provider#20](https://github.com/odango-chan/ca-provider-5gc/issues/20) 拥有计算/profile/产物，Provider#17 提供 NF context；完整 codec/向量/调用面尚未实现，绝不在本 Tool 内发 SBI 或读取 NF |
| sbi.amf.n1n2.transfer / mutation | 当前 context、受限 responseArtifactRef、lifecycle → operationRef 与真实 response | Provider#20/Fabric#70；验证相同实例/产物有效性与唯一 sender；不把 SMF response 冒充本调用响应 |
| createdsession.operation.reconcile / read_only | 原 operationRef、lifecycle → COMMITTED/NOT_COMMITTED/UNRESOLVED | Runtime#172；只对已记录操作取证和调和，不暗中重新变更；操作身份必须在任何 unknown 路径可恢复 |
| fivegc.session.evidence.await / read_only | 本次 transfer operationRef、当前 context/lifecycle、所需证据类别 → 来源可用性结果 | Runtime#172/Fabric#70 及 UE source owner；按执行期限有界等候，SUCCEEDED 只说明材料可用，不授予 Predicate PASS；caller timeout 不改业务期限 |
| fivegc.session.resource_responsibility.transfer / mutation | lifecycle、终止/成功 disposition → 可恢复 operation/receipt | Provider#19 的持续资源服务与 Runtime#172；内部责任移交，无隐藏 NF 清理，持久责任不能直到此步骤才首次建立 |

所有变更结果要求 operationRef；NOT_COMMITTED 不由“HTTP 非 2xx”直接推导。备选 SMF ACTIVATING 在阶段检查前写 up_cnx_state，不能伪装为只读 codec；主流程的 response.prepare 仅 local_compute；SMF/AMF 的实际每个 SO 仍按一次调用一次发送，mandatory SCP。

## 4. Predicate 与 Observation 反查

predicates.yaml 中新增 source 名称/字段均是本候选的未闭合依赖，不能冒充当前真实 Provider 已输出的 DTO。将“bindingStatus=CURRENT”等标签写进草稿不等于已证明实例；owner 必须给出其原生来源、字段/schema、关联/失效/一致性及正反资格。当前真实 schemas 不足时保持 UNKNOWN，不拼新 established snapshot。

| Predicate/source 类别 | 必需来源与边界 |
| --- | --- |
| ingress / policy context / N1/N2 SM delivery context | 精确 AMF 初始 source + action fence、当前实例、真实分配/默认 flow、consumer/callback 与唯一 sender 权限；源/读取 port 尚待 owner 发布 |
| UDM usable / sbi.operation.result | 复用 A 候选的真实 transient fact；acquisition 必须精确锁定当前 get-sm-data 操作，不能按同 UE/PSI/时间找“最近结果”。ToolResult 与该 Observation 的 request/record/digest 必须同源；脚本不主动获取材料 |
| SDM/PCF ownership | 实际创建结果、资源 native identity、callback 与持久责任记录；Location 和新 invocation 不能独自证明隔离 |
| N4 initial / forwarding | 当前 UPF 的目标 flow/PDR/FAR/QER/实际 tunnel 和相应阶段证明；现有 summary 没有全部字段，snapshot-consistency=NOT_PROVIDED，不能由 SMF 缓存或 PFCP send 判 PASS |
| response artifact / AMF transfer | 可信 codec/profile、输入/产物 digests、实际 sender、响应 origin、Content-ID/MIME/part 关联与 current-instance；AMF 200 可仍缓存，202/未知 cause 保持未解决 |
| RAN setup | AMF→SMF 的真实 SBI 结果，由 Provider#20 获准 N2 SM decoder 从 Fabric#70 保留的精确源 bytes/关联提供 typed 语义，或使用受支持 owner 投影；Initial Context Setup 与普通 Setup 两条来源均覆盖。类型标签不足证明所需 QFI/部分失败；不让模型自行解码 N2 |
| UE configuration | 独立精确 UE/session 的真实 SM 状态/已选配置；当前没有正式可用 source，不把日志字符串或 NAS sent 当证据 |
| resource responsibility | 持久服务已确认承接所有已知/未知资源及晚到事件；进程重启、迟到通知和不确定变更仍可恢复 |

历史 transaction/RAN 事实使用较长 acquisition freshness 窗口，不刷新原事件时间，也不授予旧实例有效性。当前 UE/N4/context 使用 5s 候选窗口。正式 binding 仍须按每个主张的生命周期和执行期限冻结；没有精确 instance/operation 关联时不复用。该处不是已发布 retention policy。

有界 await 的数据/事件 port、执行期限、重启恢复和结果投递尚未实现。它不能伪造事件，也不能解析 N2 或替原 SMF 对 AMF 响应。source 不可用、超时、旧事件/实例歧义为 UNKNOWN；明确网络反证为 FAIL。

## 5. 当前验证范围

26 个 case.yaml 是按当前 Case schema 编写的合成资格场景草稿，覆盖完整目标、缺失/歧义、真实拒绝、资源归属、旧实例、200 缓存/202、RAN/N4/UE、read-only UDM uncertainty、mutation unknown/reconcile 和移交。它们不是已执行的 Mock Runtime/协议/live 用例；fixtures 中的权威标记、Tool 可用和 PASS 只描述挑战输入。

当前本地 candidate 将 `get-sm-data` 的 `OUTCOME_UNKNOWN` 分支改为 `SAFE_STOPPED`，并增加 `26-udm-read-unknown` Case；原因是现有 Runtime 只在 action-level unknown path 做安全停止，不能把该 read-only uncertainty 表达成 mutation reconciliation。2026-10-29 使用 ca-skill-toolchain 本地候选 `codex/createdsession-skill-local-predicates-128`@`9993c413dff7a897907ae7d228dc70606f023ad9` 重新验证：`5gc-file-transfer` compile 为 `VALID`、0 findings；仓库 `make verify` 通过；全部 17 个 CreatedSession Cases 的 deterministic `planning-test` 通过，14 个含选定 Procedure 的 Case 另通过 `mock-run`。此前 19 个 `CAPABILITY_NOT_FOUND` 属于不同的 Toolchain candidate/revision，不能代表本次 checkout。详细命令、digest 和逐 Case 结果见 [2026-10-29 Toolchain consumer qualification](../artifacts/reviews/20261029-createdsession-toolchain-consumer-qualification/README.md)。该结果是未确认合入的 Toolchain 候选上的本地 compile/Case 证据；不表示 Toolchain 已进入 main、Skill 已获得生产资格、Capability 已有生产 Admission，或 Runtime/真实网络已执行。

当前 Case fixtures 不能提供新增 Capability 的真实 typed node outputs/source。因此后续资格必须由正式 owner Tool adapters/Qualification composition 供应这些输出和 evidence，不能扩展 case.yaml 私有字段、绕过 Artifact 或将 fixtures 当真实成功。

实际检查和环境 blocker 见 [本轮 manifest](../artifacts/reviews/20261022-createdsession-skill-source/validation.json)。需要运行的 owner 入口保持：

```bash
python3 -B scripts/verify.py --compile skills/establish-pdu-session
make verify
```

源码/Schema/本地纯计算检查、Compiler/reference closure、Mock/SQ、真实 WSL2 验收分别记录。只有后者满足所需主张，才可报告对应业务成功；当前不注册、不发布 qualified Artifact、不扩大模型 Tool 可见面。
