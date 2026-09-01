---
name: 5gc-file-transfer
description: 为 SBI-proxy gateway 驱动的大文件传输准备和释放 5GC 网络资源；验证参与 UE 的注册与 PDU Session 状态，准备 edge cache、Virtual Group 和按需 QoS boost，不处理文件内容和用户交互。
---

# 5GC File Transfer

## 目标

为 gateway 驱动的大文件传输准备所需的 5GC 网络资源，并在传输结束或取消后释放 Virtual Group。

本 Skill 只负责核心网编排，不负责文件传输业务本身。

## 使用时机

用于 gateway 归一化后的以下两类请求：

- `prepare_transfer`：对应 `[TASK: 5GC-FILE-TRANSFER]`；
- `release_group`：对应 `[TASK: 5GC-VG-RELEASE]`。

`[TASK: 5GC-INTENT]` 不属于本 Skill。通用 5GC 意图应由独立 Skill 处理，避免把通用 SBI 权限并入文件传输能力边界。

## 职责边界

Gateway 负责：

- 收集接收方确认；
- 文件上传、绑定和下载；
- 用户可见消息；
- 决定何时激活或结束传输；
- 将原始 gateway task 归一化为本 Skill 的结构化请求。

本 Skill 负责：

- 证明 sender 与全部 receiver 已注册；
- 证明 sender 与全部 receiver 具备活动 PDU Session；
- 准备 edge cache；
- 创建 Virtual Group；
- 绑定成员 IMSI/IP；
- 仅在原始意图明确表达紧迫性时申请 QoS boost；
- 在 release 请求中释放指定 Virtual Group。

本 Skill 不读取或写入文件字节，不向用户发送消息，不启动或停止网元进程，不修改订阅数据库，不调用 Wi-Fi 能力。

## 意图归一化

`prepare_transfer` 在进入确定性 Procedure 前，必须把原始用户意图归一化为：

- `urgent`：明确包含 ASAP、urgent、quickly、hurry、fast 或其它语言中的等价紧迫表达；
- `normal`：普通传输请求。

“大文件”本身不等于 `urgent`。

归一化后的 `urgency` 是本次执行的结构化输入。Procedure 不在执行中重新解析自然语言。

## 处理原则

1. FILE_TRANSFER 和 VG_RELEASE 均使用已治理的确定性 Procedure，不由模型临时拼装 Tool 调用序列。
2. 动态 receiver 数量不由模型维护循环。`transfer.participants.*` 观察能力接收规范化成员集合，由 Provider 对成员进行确定性逐项取证。
3. 具体 `nf_udm_*`、`edge_cache_*`、`vg_*`、`pcf_*` Tool 名称属于 Provider/Binding，不写入 Procedure 作为稳定语义。
4. `virtual_group.activate` 不属于本 Skill；是否激活由 gateway 根据用户确认决定。
5. QoS boost 仅允许在 `urgency=urgent` 的确定性路径出现，且预算最多一次。
6. 具有副作用的动作返回 `OUTCOME_UNKNOWN` 时不得盲目重试；必须先进入对应 reconcile 路径或安全停止。
7. `vg_release` 的“已释放/不存在”由 Capability outcome normalization 归一为成功语义，不要求模型解释字符串。
8. gateway 要求的 `vg-YYYYMMDD-NNN` 文本格式属于输出适配层；Runtime/Skill 使用结构化 `groupId`。
9. Gateway 提供的成员 IMSI/IP 在请求归一化和 Schema 校验通过后视为本次请求的权威输入；Skill 不根据内置手机表覆盖动态值。
10. 成功不是“最后一个 Tool 返回成功”，而是 `file_transfer.request.satisfied` 得到可信证据确认。

## 参考资料

核心编排模型由 `references/preload/orchestration-model.md` 随 Skill 加载。

当前 SBI-proxy 环境中 Capability 与旧 NF/VG/PCF Tool 的迁移映射见 `references/on-demand/sbi-proxy-provider-mapping.md`。该文件只用于 Provider 实现和迁移说明，不是 Runtime 的 Binding Truth Source。

Procedure、Predicate、预算、UNKNOWN 和恢复语义以 `assurance/`、Runtime Capability Contract 与 Provider Binding 为准。

## 简短示例

- 普通传输：验证全部参与 UE → edge cache → create VG → assign members → 验证目标，不执行 QoS boost。
- 紧急传输：与普通路径相同，但成员绑定成功后最多执行一次 QoS boost。
- VG release：只执行受治理的 release；若 mutation outcome 不确定，进入 reconcile，不重放 release。
