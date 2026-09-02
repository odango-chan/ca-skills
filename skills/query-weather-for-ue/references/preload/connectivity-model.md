# 连接状态模型

本 Skill 只依赖两个与规划相关的判断：

- `user_plane.connectivity.available`：从 UE 业务视角判断用户面是否可用。
- `ue.registered`：UE 是否满足执行前置。

`PDU Session 存在` 不能直接推导为 `用户面连接可用`。本 Skill 不把 `pdu_session.state` 或 `ue.registration` 带入 PlanningContext，避免与两个三值判断形成第二套状态真相。连接可用需要新鲜、可信的 Evidence；必要时通过 `user_plane.probe` 主动取证。

取值遵循三值语义：

- `PASS`：证据足以证明成立。
- `FAIL`：证据足以证明不成立。
- `UNKNOWN`：证据不足、过期或冲突。
