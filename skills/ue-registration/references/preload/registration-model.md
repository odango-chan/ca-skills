# Registration model

UE Registration 的业务目标是建立可信的 UE 注册关系，而不是完成某一条 NAS、NGAP 或 SBI 消息。

模型只需理解以下业务阶段：请求、身份可信、鉴权成功、安全上下文建立、注册上下文准备、注册完成、最终状态验证。每个阶段都必须由独立观察证明；阶段性 `COMMITTED` 不等于整个 Skill Goal 成功。

UE、NG-RAN、AMF、AUSF、UDM/UDR 是协议参与方，不是模型要逐条调用的工具。具体 Action、transition、Predicate、失败结果和恢复边界只以机器 Contract 与 Runtime 为准。
