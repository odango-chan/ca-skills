---
name: ensure-session-qos
description: 为目标 UE 收敛满足指定 DNN、S-NSSAI 和 5QI 要求的 PDU Session，并以独立用户面证据确认最终状态。
---

# Ensure Session QoS

当业务目标是确保目标 UE 获得指定 DNN、S-NSSAI 和 5QI 的数据连接时使用本 Skill。
Session 与 QoS 的创建、修改、观察和调和是受 Runtime 治理的底层能力，不等同于
Skill Goal。

使用时遵守以下边界：

1. `ue.registered` 未被可信证据确认 `PASS` 时，不启动 Session 写操作。
2. 当前 Session/QoS 已满足目标时只验证，不重复写入。
3. Session 状态未知时先观察或查询，不根据猜测维护第二套状态真相。
4. 副作用动作 `OUTCOME_UNKNOWN` 后必须先调和；不得 blind retry。
5. `COMMITTED` 只证明动作提交，不证明 Skill Goal 已满足。
6. 最终成功必须由独立证据确认 Session、QoS 和用户面均满足；用户面失败时不擅自寻找恢复动作。

请求字段和确定性执行流程以 `assurance/` 机器契约为准；Provider、Tool、ObservationBinding
和 acquisition 不属于 Skill source。
