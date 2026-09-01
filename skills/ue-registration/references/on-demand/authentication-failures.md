# Authentication failures

仅在 Authentication 阶段出现异常并需要进一步解释时读取。

Synchronization failure 表示 UE 与认证侧序列状态可能不同步，不等价于 subscriber 不存在。Authentication response mismatch 表示鉴权目标未满足，不能继续建立 Security Context。AUSF unavailable 属于依赖不可用，也不等价于 UE 主动拒绝鉴权。

如果认证 mutation 的副作用状态无法确定，应保留 `OUTCOME_UNKNOWN`。当前已治理 Registration Procedure 对这种结果安全停止，不允许仅凭本文建议直接重试。

本文只解释异常语义，不定义执行 transition、补偿策略或 Authorization 例外。
