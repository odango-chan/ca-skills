# ue-registration 包说明

本文面向 Skill 作者、维护者和评测人员；运行时模型入口见 [`SKILL.md`](SKILL.md)。

## 当前定位

`ue-registration` 已作为正式 Skill Package 进入 `skills/`，用于验证复杂 Registration Procedure 的 Authoring、Compiler、Planning、Mock Execution、SIMULATED_TOOL Evaluation、Reference 加载和 shared Runtime 兼容边界。

当前 Registry 中的 `amf/*` ToolRegistration 全部是 `conformance.status=fixture`。它们提供引用闭包、绑定语义和 reference simulation 的业务级状态转换，不代表 ConnectionAgent 已接管真实 AMF，也不代表已经完成 3GPP conformance、真实 AUSF/UDM 交互或 live network acceptance。

## 当前已治理范围

- Initial Registration 的身份解析、鉴权、安全上下文、Registration Context 准备和注册收尾；
- 已注册 UE 的最终状态与上下文一致性验证；
- preload / on-demand Reference；
- 阶段 Predicate 与最终业务 postcondition；
- mutation `OUTCOME_UNKNOWN` 的 fail-safe 停止，禁止盲目重试；
- Initial Registration 在鉴权验证通过后提供受治理的 Procedure Patch Point，用于插入只读检查/观察能力；
- Simulation Planner 在能确定唯一基础 Procedure 时可使用 `ProcedurePatchProposal`，而不是让模型重写整个注册流程；
- `reference-5gc-simulation-v1` 提供最小 Registration 业务状态链，使 `initial-registration` happy path 可以在 SIMULATED_TOOL 模式下执行和验证。

## ProcedurePatch 定制样板

基础 `initial-registration` Procedure 保持不变。当前在 `verify-authentication` 的 `PASS` 边声明 `after-authentication` Patch Point；只有通过该扩展点编译出的 Patch 才能把额外动作插入到安全建立之前。

```text
authenticate
    ↓
verify-authentication
    │ PASS
    ▼
[ after-authentication ]
    │
    ├─ 无 Patch ───────────────→ establish-security
    │
    └─ 有 Patch → extra-action → establish-security
```

Patch Point 由 Skill 作者控制允许的操作、effect 和结果路由。当前样板只允许 `read_only` Action；插入能力必须提供与扩展点一致的 `SUCCEEDED / FAILED / UNKNOWN / DENIED` 结果集，并分别按 Skill 已声明的规则继续、失败或进入 unresolved。Patch 作者不能自行覆盖这些失败语义。

### Simulation Run

当当前 PlanningContext 能确定 `initial-registration` 为唯一基础 Procedure，且 Planner 支持 Patch 模式时，Platform 使用：

```text
PlanningContext
      ↓
确定性选择 Base Procedure
      ↓
LLM → ProcedurePatchProposal
      ↓
Platform 补齐 base / source / candidate status
      ↓
ProcedurePatch Apply
      ↓
Effective Procedure
      ↓
原有 Procedure Validator / Runtime
```

模型只能决定 `USE_BASE / APPLY_PATCH / PLANNING_BLOCKED`，以及合法 Patch operation 的 Point、Capability 和输入。基础 Procedure、Patch Point、失败路由、provenance 和 Qualification 状态均由 Platform 控制。

`cases/01-initial-registration-happy/evaluation-scenario.yaml` 是当前 Registration 的 reference Simulation 场景。reference provider 只维护下列业务级 ground truth：

```text
identityResolved
      ↓
authenticated
      ↓
securityEstablished
      ↓
contextReady
      ↓
registered + contextConsistent
```

这些状态只用于驱动 Skill Predicate 和验证 Harness/Runtime 行为，不模拟 NAS、NGAP、Nausf、Nudm 等真实消息交互，也不声称是 AMF 内部状态机。`OUTCOME_UNKNOWN` 仍严格服从当前 Skill 的 `safe-stopped` 失败语义；reference provider 不为 Registration mutation 私自增加 reconcile 路径。

### 固定流程

客户通过 Web/API 保存的是完整 `ProcedurePatch`。保存后 Patch 是确定性输入，不需要再次调用 LLM；经 Qualification 晋升后的 Variant 才能进入后续确定性的 Scene Run 使用路径。

完整示例见 [`examples/`](examples/README.md)。真正执行前，客户自定义 API 仍必须先注册为 Capability、完成 Tool Binding，并纳入 Skill Contract 的 allowedResources。若客户只是把原有鉴权换成自己的实现，应优先使用 Binding Override，而不是 ProcedurePatch。

## 暂不声明

当前版本不声明：

- Mobility Registration / Periodic Registration；
- 真实 AMF/AUSF/UDM Provider；
- NAS/NGAP/Nausf/Nudm 级 Registration 协议模拟；
- AMF 内部状态窗口故障注入；
- Registration mutation 的通用自动 Reconciliation；
- 任意节点、任意副作用的流程改写；
- 生产认证或正式 Benchmark 结论。

当前 reference simulation 的职责只是让 Registration Skill 的业务流程、Patch、Predicate、失败语义和 Runtime 链路能够被重复验证。真实 Registration Recovery 后续仍应在 shared Runtime 的 generic Recovery Contract 收口后补齐，而不是在 Reference 或 Skill-local 脚本中另造恢复状态机。
