# 天气服务语义

Weather Tool 属于外部业务 Tool，不是 3GPP 核心网能力。

本 Skill 使用稳定语义 `external.weather.query`。运行环境可以把它绑定到不同运营商或测试 Weather MCP Tool。

输入至少包含：

- `city`
- `unit`

本参考包使用摄氏度 `celsius`。

成功的原始输出必须同时包含非空 `city`、有限数值 `temperature` 和非空 `condition`。本地规范化 Tool 只做去除首尾空白和数值归一化；任何缺字段、空字符串或非有限温度都明确失败，不能补 `unknown` 或 `0.0`。

调用硬前置：

`user_plane.connectivity.available=PASS`

Tool 可发现但前置不满足时，PlanningContext 可以显示资源存在，但 `invocable=false`。模型不得据此直接调用。

`external.weather.query=SUCCEEDED` 只表示外部调用完成，不等于整个 Skill 成功。规范化完成后必须通过 `verify-weather-result` 独立求值 `service.weather.query.succeeded`，只有 PASS 才能进入 `SUCCEEDED` terminal。
