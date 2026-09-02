---
name: ensure-session-qos
description: 为目标 UE 收敛满足指定 DNN、S-NSSAI 和 5QI 要求的 PDU Session，并以独立用户面证据确认最终状态。
---

# Ensure Session QoS

当业务目标是确保目标 UE 获得指定 DNN、S-NSSAI 和 5QI 的数据连接时使用本 Skill。

本 Skill 的目标是最终存在满足请求 QoS 的 PDU Session；单次 create/modify 成功不等于业务目标完成。
用户面连接性属于最终业务成功条件，但连接恢复不是本 Skill 的主动目标。

使用时遵守以下业务边界：

1. 未确认目标 UE 已注册时，不启动 Session 写操作。
2. 当前 Session/QoS 已满足目标时只验证，不重复写入。
3. 不根据猜测维护第二套 Session 状态真相。
4. 具有副作用的动作结果未知时，不盲目重试。
5. 最终成功必须由独立证据确认 Session、QoS 和用户面均满足。

请求字段和确定性执行流程以 `assurance/` 机器契约为准；Provider、Tool、ObservationBinding
和 acquisition 不属于 Skill source。
