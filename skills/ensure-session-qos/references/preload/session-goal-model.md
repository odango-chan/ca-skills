# Session goal model

本 Skill 的主动目标是“最终存在满足请求 QoS 的 PDU Session”。创建、修改、查询和调和只是实现目标的动作，不能独立代表成功。

三个后置条件分别回答：会话是否存在、请求的 QoS 是否满足、用户面是否真实可用。写操作返回 COMMITTED 后仍必须重新观察这三个 Predicate；用户面连通性是最终成功门禁，不是本 Skill 主动修复的 requirement。

因此，Session 和 QoS 已满足但 `user_plane.connectivity.available=FAIL` 时，本 Skill 选择零写入验证路径并返回 FAILED。连接恢复属于未来 `ensure-connectivity` 或 `restore-connectivity` 的目标边界。

Release/断开连接是相反且具有破坏性的独立目标，不属于本 Skill。需要覆盖释放流程时，应另建 `ensure-session-absent`。
