# ue-registration

这是 target-state 的 assurance-enabled executable Skill source。

## Source contract

- `SKILL.md` 只包含选择条件、Registration 业务阶段、不可猜测的边界和模型输出边界。
- `assurance/contract.yaml` 只声明业务目标、request schema、稳定 Capability、前置/后置条件和预算。
- `assurance/procedure.yaml` 是确定性流程；协议消息由 Capability 实现内部处理，不拆成模型 Action。
- `assurance/predicates.yaml` 用 typed ObservationBinding 输入和 CEL evaluator 计算 tri-state Predicate。
- Evidence acquisition、freshness、Evidence Gate、ProviderBinding、UNKNOWN/reconcile 属于 Runtime，不在本 Skill authoring 中维护。

最终注册验证使用 `ue.registered` 与 `ue.registration_context.consistent` 两个独立 Predicate。目标源不包含 `assurance/evidence.yaml`，也不把 `ue.registration.query` 伪装成 Procedure query Action：当前 proof read 由 Runtime ObservationBinding 提供。

## Qualification cases

`cases/` 覆盖 happy path、Capability 缺失、mutation `OUTCOME_UNKNOWN`、最终 postcondition 失败和 Action 被拒绝。它们是 Qualification 输入，不是 Runtime contract 的第二份定义；mock outcome 只用于确定性测试。

当前没有 ProcedurePatch 示例，因为本 target contract 尚未声明动态流程改写；若未来启用，应由独立 Variant/Patch contract 重新纳入，而不是恢复旧 snapshot。
