# Security failures

仅在 Security Context 建立阶段出现异常时读取。

需要区分明确的 UE reject、完整性校验失败、依赖超时和结果未知。Authentication 已成功不能被用来推导 Security Context 已建立；最终状态必须由独立 Evidence / Predicate 证明。

如果安全建立 mutation 的结果为 `OUTCOME_UNKNOWN`，当前已治理 Procedure 安全停止，不允许根据 Authentication 已成功这一事实推测安全上下文已经提交。

本文只解释异常语义，不赋予模型绕过 Authorization、Assurance 或 Runtime policy 的权限。
