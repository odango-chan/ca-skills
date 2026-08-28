# Registration model

UE Registration 的业务目标是建立可信的 UE 注册关系，不是完成某一条 NAS、NGAP 或 SBI 消息。

可以用下面的阶段模型帮助理解业务，但它不是 executable state machine：

`Registration requested → Identity resolved → Authentication succeeded → Security established → Registration context ready → Registration finalized → Registration verified`

典型参与方包括 UE、NG-RAN、AMF、AUSF、UDM/UDR。参与网元不是 Agent Action。一个稳定 Capability 可以在实现内部跨多个网元完成一组协议交互，并把底层消息作为 Protocol Event 记录。

关键边界：Authentication succeeded 不代表 Security Context 已建立；Security Context established 不代表 Registration Context 已准备完成；Registration Accept sent 不代表 Registration Complete 已确认；Capability COMMITTED 不代表整个 Skill Goal 已成功。

具体 Action、transition、Predicate、失败结果和恢复边界只以机器 Contract 与 Runtime 为准。
