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

1. 目标 UE 必须具备可信的注册状态，且天气查询依赖目标 UE 用户面连接。
2. PDU Session 存在并不等于用户面连接可用；不要猜测网络状态。
3. 天气结果不完整、为空或字段非法时明确失败，不伪造业务值。
4. 当前没有可用且合规的天气能力时，不生成不可执行请求。

## 参考资料

需要理解 Weather Tool 的输入、输出或调用前置时，按需读取 `references/on-demand/weather-service-semantics.md`。

Procedure、Predicate、动作预算和恢复语义以 `assurance/` 下的机器契约与 Runtime contract 为准；Reference 不维护第二套执行状态机。

## 简短示例

- `user_plane.connectivity.available=PASS`：直接查询天气并验证业务结果。
- Connectivity 为 `FAIL`：先满足连接前置，再查询天气。
- Connectivity 为 `UNKNOWN`：先观察；若写操作结果未知，先调和而不是重试。
