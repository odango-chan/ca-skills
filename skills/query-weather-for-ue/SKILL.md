---
name: query-weather-for-ue
description: 在满足目标 UE 数据连接前置条件后查询指定城市天气；连接未就绪时，根据可信状态选择连接收敛、探测或调和路径。
---

# Query Weather for UE

## 目标

完成面向目标 UE 的天气查询，并在调用天气服务前确认用户面连接可用；Tool 调用成功本身不等于业务目标完成。

## 使用时机

当用户需要查询天气，且该业务要求通过目标 UE 的数据连接访问外部天气服务时使用本 Skill。

## 处理原则

1. `ue.registered` 是执行前置；`FAIL` 时不执行，`UNKNOWN` 时不根据猜测继续写操作。
2. 不把“PDU Session 存在”或单次 Session 动作成功等同于“用户面连接可用”。
3. `user_plane.connectivity.available=PASS` 时可直接查询天气。
4. Connectivity 为 `FAIL` 时，可使用本 Skill 已声明的连接收敛能力恢复前置条件。
5. Connectivity 为 `UNKNOWN` 时优先补齐观察证据，不根据推测直接执行写操作。
6. 具有副作用的连接动作返回 `OUTCOME_UNKNOWN` 时必须先调和，不得盲目重试。
7. Weather Tool 可发现但调用前置未满足时，不得直接调用。
8. Weather action 和本地结果规范化完成后，仍需独立验证 `service.weather.query.succeeded`。
9. 原始天气结果缺少必需字段、字符串为空或温度非法时明确失败，不注入默认业务值。
10. 当前没有可用且合规的 Capability / Tool 时，不生成不可执行 Procedure。
11. 本 Skill 不直接访问 SMF、UPF 私有接口，也不在脚本中隐藏连接控制流程。

## 参考资料

“Session 存在”和“连接可用”的区别由 `references/preload/connectivity-model.md` 随 `load_skill` 一次装配，无需额外调用 `read_reference`。

需要理解 Weather Tool 的输入、输出或调用前置时，按需读取 `references/on-demand/weather-service-semantics.md`。

Procedure、Predicate、动作预算和恢复语义以 `assurance/` 下的机器契约与 Runtime contract 为准；Reference 不维护第二套执行状态机。

## 简短示例

- `user_plane.connectivity.available=PASS`：直接查询天气并验证业务结果。
- Connectivity 为 `FAIL`：先满足连接前置，再查询天气。
- Connectivity 为 `UNKNOWN`：先观察；若写操作结果未知，先调和而不是重试。
