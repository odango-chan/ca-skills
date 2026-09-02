---
name: ue-registration
description: 将目标 UE 收敛到可信 REGISTERED 状态；用于 Initial Registration 或验证现有注册上下文，不把单条协议消息或单次 Capability 成功等同于注册成功。
---

# UE Registration

选择本 Skill 的条件：目标是 Initial Registration，或需要确认 UE 的注册状态及网络侧注册上下文一致性。

Registration 的业务阶段是身份可信、鉴权成功、安全上下文建立、注册上下文准备、注册完成和最终状态验证。NAS、NGAP、SBI 等协议消息是实现内部的 Protocol Event，不是模型需要逐条编排的 Action。

模型必须区分阶段性成功与最终业务成功：Authentication 不证明 Security Context，Security Context 不证明 Registration Context，Registration Accept 不证明 Registration Complete。最终目标必须由 Runtime 提供的 canonical typed Observation 经 `ue.registered` 与 `ue.registration_context.consistent` 两个独立 Predicate 共同证明。

不能猜测未观察到的状态，也不能把 `COMMITTED` 推导为 Skill Goal 已满足。副作用 Action 返回 `OUTCOME_UNKNOWN` 时不得盲目重试；在没有可信 Reconcile Capability 的当前版本，交给确定性执行面安全停止。

模型最终只提交业务 request 或选择 `ue-registration` Skill target。Runtime 进入确定性的 Procedure 并执行其中声明的 Capability；模型不逐步选择 `resolve`、`authenticate`、`establish`、`prepare` 或 `finalize`。身份、协议栈和具体网络厂商实现由 governed execution plane 处理。
