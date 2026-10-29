# CreatedSession Skill 源码候选与依赖反查

状态：Proposed v0.1；owner：[ca-skills#20](https://github.com/odango-chan/ca-skills/issues/20)。

语义评审：[2026-10-22 完整评审](../artifacts/reviews/20261022-createdsession-skill-review/README.md)针对当时的 `d3576dc` 判定 **CHANGES_REQUIRED**。之后的源码提交已修正 admitted fact 绑定、UDM 读取 lineage、read-only UNKNOWN 的安全停止、Case 期望、AMBR/QoS 传递及局部类型检查；这些修正不构成 Runtime/Fabric owner contract 或资格通过。当前仍因正式 owner Mutation Capability/Admission、四个 post-transfer Observation、跨组件来源关联和真实集成证据未闭合而保持 Draft。

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
| fivegc.session.evidence.await / read_only | 本次 transfer operationRef、当前 context/lifecycle、所需证据类别 → 来源可用性结果 | Runtime#172/Fabric#70 及 UE source owner；按执行期限有界等候，SUCCEEDED 只说明材料可用，不授予 Predicate PASS；caller timeout 不改业务期限 |
| fivegc.session.resource_responsibility.transfer / mutation | lifecycle、终止/成功 disposition → 可恢复 operation/receipt | Provider#19 的持续资源服务与 Runtime#172；内部责任移交，无隐藏 NF 清理，持久责任不能直到此步骤才首次建立 |

Procedure 的不确定变更使用 Toolchain 原生 `reconcile: <mutation-node-id>`，关联原 mutation 的 invocation 并由 Runtime Reconciler 处理；它不是 Capability、Provider read 或独立 operationRef 查询。Toolchain `882ac43` 已识别该语法，但当前编译因 mutation owner 尚无正式注册契约而给出 `PR5_VNEXT_RECONCILE_EFFECT_INVALID`。所有变更结果要求 operationRef；NOT_COMMITTED 不由“HTTP 非 2xx”直接推导。备选 SMF ACTIVATING 在阶段检查前写 up_cnx_state，不能伪装为只读 codec；主流程的 response.prepare 仅 local_compute；SMF/AMF 的实际每个 SO 仍按一次调用一次发送，mandatory SCP。

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

### Post-transfer Observation refs: owner binding not identified

The four child predicates consume these candidate refs, but no versioned owner contract or native source was found at the current Provider `d2070c3fdcbafe7fd53d630a7379c4c3f64aa156`, Fabric `1ae8338e19902668a2947c7b47d39b06d631acbf`, or Sandbox `460c4628eb54a97de2485e1b41ed76db9ba22d23` heads. Exact-ref searches across those checkouts returned no matches. These names remain unversioned Skill-side candidates, not registered observations.

| Candidate observation ref | Predicate | Current owner/source status |
| --- | --- | --- |
| `createdsession.ran_setup_result` | `createdsession.ran.setup_accepted` | Provider N2 decoding of Fabric's preserved UpdateSMContext source is only a candidate; authenticated native source and association contract are unidentified. |
| `createdsession.n4_forwarding_resources` | `createdsession.n4.forwarding_ready` | UPF PDR/FAR/QER and tunnel-stage proof source/version is unidentified; summary evidence cannot establish current forwarding readiness. |
| `createdsession.ue_sm_configuration` | `createdsession.ue.configuration_accepted` | Independent current UE/session configuration source and schema version are unidentified. |
| `createdsession.resource_responsibility` | `createdsession.resources.managed` | Persistent owner and transferable lifecycle receipt contract/version are unidentified; a Provider lifecycle candidate is not accepted proof. |

Keep all four bindings unresolved/UNKNOWN until the owning repository publishes exact schema/version, source identity, correlation, freshness/consistency, and positive/negative qualification evidence. Do not satisfy them with fixture strings or inferred operation outcomes.

#### Executable owner task records

The entries below satisfy the nine-field handoff required for implementation. Names shown first are current Skill candidate refs; formal Observation name, type/version and authority remain `NOT_IDENTIFIED`, so none may be registered or consumed as owner truth yet.

1. **RAN setup result — candidate `createdsession.ran_setup_result`, channel `state`; formal identity/version `NOT_IDENTIFIED`.** Producer/repository: AMF-originated UpdateSMContext source through Fabric plus a trusted Provider decoder; exact producer contract unresolved. Acquisition: authenticated Fabric source query and Provider typed N2 result decoder; neither is wired as a production source adapter. Consumer: Predicate `createdsession.ran.setup_accepted`, requiring `ACCEPTED`, required flow match and current instance binding; final Outcome/Reconcile remains Runtime-owned and separate. Current state: Skill candidate only; Fabric has encrypted source capture and local parsing, Provider has an unconnected source-port validator, no registered Observation/schema. Instance association: candidate scope has UE, PSI and ingress only; must join exact invocation, transfer operation/transaction, source record, AMF/SMF identities and current session instance. Integrity/freshness: authenticate source; verify request/source/association/payload digests; reject duplicate, stale, partial or ambiguous records; candidate 1h freshness is unapproved. Tests/acceptance: Fabric SBI package/parser/store tests and Provider synthetic binding validator exist; missing joined authenticated-source and ambiguity qualification. Minimal next step: freeze a versioned Fabric selector/response projection and Provider adapter contract, then add exact-binding cross-owner integration tests.

2. **N4 forwarding resources — candidate `createdsession.n4_forwarding_resources`, channel `state`; formal identity/version `NOT_IDENTIFIED`.** Producer/repository: authoritative UPF/SMF owner-state source; Provider owns the adapter, while exact source/version and Runtime Observation contract need confirmation. Acquisition: fresh exact SMF/UPF N4 pair join plus PFCP/PDR/FAR/QER and tunnel state; a summary or transfer response is insufficient. Consumer: Predicate `createdsession.n4.forwarding_ready`, requiring current binding, required flow, downlink tunnel match and forwarding gates; final Outcome remains separate. Current state: Provider reads/joins selected N4 resources for operation context, but no post-transfer full forwarding Observation is registered. Instance association: exact current session instance plus invocation/operation/lifecycle and N4 pair; reject mismatched pair or stale generation. Integrity/freshness: source digests, consistent snapshot or bounded reads, unique flow/tunnel match, explicit unavailable/ambiguous outcomes; candidate 5s freshness is unapproved. Tests/acceptance: Provider Open5GS context tests cover pair joins and selected N3 PDR; missing post-transfer PFCP/forwarding-gate positive and negative qualification and real endpoint evidence. Minimal next step: identify exact upstream forwarding-state surfaces and version, then implement a read-only typed adapter and consistency/ambiguity tests.

3. **UE SM configuration — candidate `createdsession.ue_sm_configuration`, channel `state`; formal identity/version `NOT_IDENTIFIED`.** Producer/repository: UE-side UERANSIM/RAN state source owner unresolved; it is not Provider or Fabric state. Acquisition: independent current UE session configuration/SM state inspection, not inferred from AMF acceptance or outbound N1/N2. Consumer: Predicate `createdsession.ue.configuration_accepted`, requiring active SM state, selected configuration match and current instance binding; final Outcome remains separate. Current state: no production adapter, owner schema or registered Observation found in authorized candidates. Instance association: exact UE identity, PSI, session generation, ingress/invocation and selected-configuration digest; reject stale state and reused PSI. Integrity/freshness: authenticated source, exact source revision/profile, bounded freshness, complete configuration and explicit missing/ambiguous/unsupported statuses; candidate 5s is unapproved. Tests/acceptance: Skill fixtures only; missing owner source tests, same-PSI/new-instance negative test and joined UE/gNB evidence. Minimal next step: identify the UE-state source owner/interface, then define a versioned read contract and implement a read-only adapter with restart/reuse tests.

4. **Resource responsibility — candidate `createdsession.resource_responsibility`, channel `state`; formal identity/version `NOT_IDENTIFIED`.** Producer/repository: durable Provider lifecycle service is a candidate for Agent-owned UDM/PCF resources; persistent owner for all late/unknown resources and its cross-resource receipt remain unresolved. Acquisition: journaled lifecycle query/transfer receipt covering every created or possibly-created resource and pending callback/event. Consumer: Predicate `createdsession.resources.managed`, requiring accepted management state, complete coverage and retained pending responsibilities; Runtime reconcile must preserve UNKNOWN. Current state: Provider persists operation intents, callback bindings/receipts and resource refs, but no accepted unified ownership-transfer Observation/schema is registered. Instance association: exact operation, invocation, lifecycle, subject, current session instance, callback/resource refs and durable-store identity; prohibit carry-over to reused PSI/new instance. Integrity/freshness: durable authenticated journal, replay-safe receipt, completeness proof, late-event retention and explicit partial/unknown state; candidate 5s freshness is inappropriate/unapproved for durable responsibility. Tests/acceptance: Provider journal/restart and callback tests exist; missing all-resource coverage, late/duplicate handoff, crash-window and formal receipt qualification. Minimal next step: define a versioned Provider responsibility receipt with resource inventory/transfer semantics, then test restart, late event, partial failure and repeated handoff without duplicate ownership.

## 5. 当前验证范围

26 个 case.yaml 是按当前 Case schema 编写的合成资格场景草稿，覆盖完整目标、缺失/歧义、真实拒绝、资源归属、旧实例、200 缓存/202、RAN/N4/UE、read-only UDM uncertainty、mutation unknown/reconcile 和移交。它们不是已执行的 Mock Runtime/协议/live 用例；fixtures 中的权威标记、Tool 可用和 PASS 只描述挑战输入。

当前本地 candidate 将 `get-sm-data` 的 `OUTCOME_UNKNOWN` 分支改为 `SAFE_STOPPED`，并增加 `26-udm-read-unknown` Case；read-only uncertainty 不进入 mutation reconciliation。针对此前伪装成 `read_only` Capability 的 recovery calls，已改为 Toolchain 原生 reconcile lineage，直接引用每个 owning mutation 节点，不再声明 `createdsession.operation.reconcile`。2026-10-29 对当前 Skills `c50681d` 使用 Toolchain PR #132 `882ac43` 验证：Root `5gc-file-transfer` compile `VALID`、0 findings；`make verify` 的 8 gates 与 8 个 Python regressions PASS；child `establish-pdu-session` compile 仍 `INVALID`，当前首先报告 `PR5_VNEXT_RECONCILE_EFFECT_INVALID`，因为 reconcile owner mutation 还没有正式注册的 CapabilityContract。当前还未能从此 early owner-contract blocker 得到完整 Capability ref finding 集。此前对 `582481c`/`9993c41` 的 19 个 `CAPABILITY_NOT_FOUND` 结果仅代表旧版自定义 reconcile 节点；在正式 Toolchain `882ac43` 上不能继续照抄该 finding 数量。

四个 post-transfer Observation refs 在当前 Provider/Fabric/Sandbox owner candidate 中仍无 schema/source 声明。不能通过在 Skill 源或 Reference Registry 伪造 CapabilityContract 消除 owner 缺口；Toolchain 将 CapabilityContract.v1 authority 指向 Runtime，而 Runtime 本 Goal 只读。完整 Skill qualification、生产 Capability Admission、Runtime/跨进程/真实网络均未通过或未运行。详细 Root/child 结果见 [2026-10-29 Toolchain consumer qualification](../artifacts/reviews/20261029-createdsession-toolchain-consumer-qualification/README.md)。

当前 Case fixtures 不能提供新增 Capability 的真实 typed node outputs/source。因此后续资格必须由正式 owner Tool adapters/Qualification composition 供应这些输出和 evidence，不能扩展 case.yaml 私有字段、绕过 Artifact 或将 fixtures 当真实成功。

实际检查和环境 blocker 见 [本轮 manifest](../artifacts/reviews/20261022-createdsession-skill-source/validation.json)。需要运行的 owner 入口保持：

```bash
python3 -B scripts/verify.py --compile skills/establish-pdu-session
make verify
```

源码/Schema/本地纯计算检查、Compiler/reference closure、Mock/SQ、真实 WSL2 验收分别记录。只有后者满足所需主张，才可报告对应业务成功；当前不注册、不发布 qualified Artifact、不扩大模型 Tool 可见面。
