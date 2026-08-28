---
name: ue-registration
description: 将目标 UE 收敛到可信 REGISTERED 状态；身份、鉴权、安全上下文和注册上下文只是达到该目标的阶段性能力，不把单条协议消息或单次 Capability 成功等同于注册成功。
---

# UE Registration

## 目标

让目标 UE 最终进入可信的 `REGISTERED` 状态，并由独立证据确认 UE 与网络侧注册上下文一致。

## 使用时机

用于 Initial Registration，或确认已经注册的 UE 是否仍具备一致的注册上下文。底层 NAS、NGAP、SBI 消息由能力实现和协议栈处理，不由模型逐条编排。

## 处理原则

1. Registration Request 只表示流程开始，不等于 UE 已注册。
2. 身份未可信解析前，不继续进入依赖可信 UE 身份的后续阶段。
3. Authentication 成功不等于 Security Context 已建立。
4. Security Context 已建立不等于网络侧 Registration Context 已准备完成。
5. Registration Accept 已发送不等于 Registration Complete 已确认。
6. Capability 返回 `COMMITTED` 只证明该动作结果，不等于 Skill Goal 已满足。
7. 最终成功必须由 `ue.registered` 与 `ue.registration_context.consistent` 的独立证据共同证明。
8. 具有副作用的注册动作返回 `OUTCOME_UNKNOWN` 时不得盲目重试；当前已治理 Procedure 直接安全停止，只有显式绑定可信 Recovery Contract 后才能继续恢复。
9. AMF、AUSF、UDM/UDR、NG-RAN 是协议参与方，不自动等价为 Procedure Action。
10. 协议消息属于 Protocol Event / Observability，不把每条 NAS、NGAP 或 SBI 消息拆成模型 Tool Call。

## 参考资料

注册阶段模型由 `references/preload/registration-model.md` 随 `load_skill` 一次装配，无需额外调用 `read_reference`。

鉴权失败和安全建立失败等长尾知识位于 `references/on-demand/`，仅在确实遇到相应问题时读取。

Procedure、Predicate、动作预算、Tool binding 和恢复语义以 `assurance/`、Registry 与 Runtime contract 为准；Reference 不维护第二套执行状态机。

## 简短示例

- UE 未注册：按身份解析、鉴权、安全建立、上下文准备和注册完成的受治理路径推进，并逐阶段验证。
- UE 已注册：不重复执行注册写动作，只验证最终注册状态与上下文一致性。
- 任一注册 mutation 返回 `OUTCOME_UNKNOWN`：安全停止，不直接重放该动作。
