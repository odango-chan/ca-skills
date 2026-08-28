# UE Registration ProcedurePatch 示例

这里演示同一个 `initial-registration` Procedure 如何被 LLM 或客户定制，而不复制或修改已发布的基础 Procedure。

## 基础流程

基础流程中的关键片段是：

```text
authenticate
    ↓
verify-authentication
    │ PASS
    ▼
establish-security
```

`initial-registration` 在 `verify-authentication/PASS` 边声明了 `after-authentication` Patch Point。该扩展点只允许插入满足下列契约的 Action：

- 操作：`insert_action_after`
- effect：`read_only`
- outcomes：必须与 Patch Point 的路由契约一致
  - `SUCCEEDED`：继续基础流程原来的目标
  - `FAILED`：进入 `failed`
  - `UNKNOWN`：进入 `unresolved`
  - `DENIED`：进入 `failed`

因此 Patch 作者只决定“插入什么能力、输入是什么”，不重新定义注册流程的失败和未知结果处理。

## 示例一：Simulation Run 中由 LLM 提议 Patch

模型原始输出不是最终 `ProcedurePatch`，而是更窄的 `ProcedurePatchProposal`：

[`llm-observe-registration-state.proposal.yaml`](llm-observe-registration-state.proposal.yaml)

这个例子使用当前 Reference Registry 已存在、Skill Contract 已允许且 PlanningContext 中可调用的 `ue.registration.query`：

```text
verify-authentication
    │ PASS
    ▼
observe-registration-state
    │ SUCCEEDED
    ▼
establish-security
```

模型只能返回：

- `USE_BASE`：基础流程已经足够，不做修改；
- `APPLY_PATCH`：选择声明过的 Patch Point、允许的操作和候选 Capability；
- `PLANNING_BLOCKED`：基础流程和所有合法 Patch 都无法满足目标。

模型不能填写 `source`、`status`、基础 Skill/Procedure、失败路由或 Qualification 状态。Platform 接收合法 Proposal 后，才物化成统一的 Candidate Patch：

[`llm-observe-registration-state.materialized.patch.yaml`](llm-observe-registration-state.materialized.patch.yaml)

其服务端固定元信息为：

```yaml
source:
  type: llm
  ref: simulation-planner
status: candidate
```

之后进入同一条确定性链：

```text
ProcedurePatchProposal
        ↓
Platform materialize
        ↓
ProcedurePatch(candidate)
        ↓
Patch Apply
        ↓
Effective Procedure
        ↓
Procedure Validator / Runtime
```

## 示例二：客户通过 Web 编辑器固定流程

[`customer-add-compliance-check.patch.yaml`](customer-add-compliance-check.patch.yaml) 表示客户在可视化编辑器中选择“鉴权后增加合规检查”。Web 后端保存的仍是相同的 `ProcedurePatch`，客户不需要手写 YAML。

保存后 Patch 是固定输入；后续应用 Patch、生成 Effective Procedure 和执行都可以是确定性的，不再需要 LLM。

## 示例三：外部客户 Capability 的 LLM Candidate

[`llm-add-enterprise-risk-check.patch.yaml`](llm-add-enterprise-risk-check.patch.yaml) 保留为“外部 Capability 已完成注册以后”的物化 Candidate 示例。它不是当前 Reference Registry 可直接运行的 Patch。

示例里的：

- `customer.registration.risk_check`
- `customer.registration.compliance_check`

都是客户侧 Capability 占位符。真正使用前，必须先完成 Capability 注册、Tool Binding，并把 Capability 纳入 Skill Contract 的 `allowedResources`。同时还必须满足 Patch Point 声明的 effect/outcome contract；任一条件不满足，Patch Compiler 都应拒绝生成 Effective Procedure。

这也保持了边界：

- 换已有步骤的实现：Binding Override；
- 在流程中新增受治理步骤：ProcedurePatch；
- 纯旁路通知/审计：Event Hook；
- 改变 Skill 的能力语义或可靠性边界：派生/新 Skill。
