# Examples

S1 暂不携带 ProcedurePatch 示例。当前 target contract 使用固定 Procedure；模型只产生业务 request，Runtime 负责 Observation、Capability dispatch 和最终 Outcome。

未来的动态流程扩展必须通过独立 Variant/Patch contract 重新声明允许的节点、Capability effect 和结果路由，并完成 Qualification 后才能加入这里。
