# ConnectionAgent Skill 编写指南

本文档面向需要新增或修改官方 Skill 的开发者，说明 `ca-skills` 仓中的编写方式、边界和验证流程。

详细 YAML 与脚本语法见：

```text
.agents/skills/create-connectionagent-skill/references/authoring-syntax.md
```

机器语法是否合法，以 `ca-skill-toolchain` 当前的 Schema 和编译器为准。

英文版：[`authoring.md`](authoring.md)

## 1. 先判断应该写什么

开始建目录之前，先判断需求属于以下哪一类。

### 可执行 Skill

当目标具有明确的产品或领域语义，并且执行过程需要确定性的保障逻辑时，使用可执行 Skill。

通常包含：

```text
SKILL.md
assurance/
cases/
```

现有参考：

- `ue-registration`
- `ensure-session-qos`
- `download-object-by-deadline`
- `query-weather-for-ue`

### 路由策略 / 模型上下文包

如果内容只是给 Agent 提供业务语义、归一化规则或路由策略，本身并不需要交给 Runtime 执行 Procedure，则使用模型上下文形式。

`5gc-intent` 是当前参考。

路由属于 Agent 自身行为，不要设计成“先执行一个路由 Skill，再由它返回另一个 Skill 的执行目标”。

### Runtime Capability

底层 Provider 动作，例如查询、创建、修改、删除，一般属于 Runtime Capability，不需要为了单个底层动作再包装一层 Skill。

如果不确定边界，可参考：

```text
.agents/skills/create-connectionagent-skill/references/skill-granularity.md
```

## 2. 标准目录结构

仅提供模型上下文的包可以很简单：

```text
skills/<name>/
├── SKILL.md
├── references/    # 可选
└── schemas/       # 可选
```

可执行 Skill 的**当前**标准结构为：

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/    # 可选
├── schemas/       # 可选
└── scripts/       # 可选
```

仓库级约束：

- `assurance/` 要么不存在，要么完整包含 `contract.yaml`、`procedure.yaml`、`predicates.yaml`；
- 当前模型没有独立的 `evidence.yaml`；
- 每个资格验证用例只使用一个 `cases/<case>/case.yaml`；
- Skill 根目录不使用 `README.md`、`MIGRATION.md`、`examples/`；
- 说明性示例放在 `references/samples/`；
- `references/` 是 Skill 自己拥有的补充材料，但**不会因为放在这里就自动进入模型上下文**；是否加载必须由 Skill/Host 的上下文策略显式决定；
- `scripts/` 继续是一等可选的 governed local-compute 资产；只有确实需要确定性本地计算时才创建，不要建空目录占位；
- 跨 Skill 的 Planner/Linker/Admission 测试 fixture 放到对应测试区域，不放在业务 Skill 的 `references/` 下；
- `skills/` 下供模型读取的 Markdown 统一使用英文；
- 不创建空目录占位。

> 2026-09-15 已冻结新的 Rule / Case lineage 设计方向，但 `rules.yaml`、`SkillRuleSet`、`ruleRefs` 尚未进入 Toolchain Schema。当前不要自行创建 `rules.yaml` 或向 Case 加未定义字段。

## 3. `SKILL.md` 写什么

`SKILL.md` 是 Skill 根目录中供模型读取的入口文件，应尽量薄，只保留会影响模型决策的内容：

- 什么情况下使用这个 Skill；
- 对应的业务或领域目标；
- 输入如何归一化、如何消歧；
- 当 Skill 确实拥有这类 payload 时，模型需要理解的输入输出语义；
- 哪些信息不能猜、哪些边界不能绕过；
- 当下一步依赖当前状态时，**哪些事实必须先获得、哪些替代推断不成立**。

对于 executable Skill，**不要为了“返回执行结果”额外发明一套 Skill-specific 模型输出 payload**。真实执行成功由 governed Procedure + SkillContract postcondition / Predicate verdict 决定。

如果某个模型 stage（例如 routing 或 semantic choice）有结构化输出，该 response contract 默认属于对应的 Host / model adapter；只有当 Skill 本身确实拥有一个独立的 model-facing semantic payload 时，才在 `SKILL.md` 中说明，并在有必要时用 `schemas/` 固定 exact shape。不要默认给每个 executable Skill 创建 `output.schema.yaml`。

默认不要把 `SKILL.md` 写成 Tool 流程说明书。通用 Agent 应根据当前 model-visible Tool 的 name / description / schema 自己选择合适的 read-only Capability。

例如更推荐写：

```text
在选择恢复动作前，必须先确认当前用户面是否可达。
不要从 PDU Session 存在这一事实推断用户面一定可达。
```

而不是默认写：

```text
Step 1: call user_plane.inspect_connectivity
Step 2: ...
```

只有在以下情况才建议在 `SKILL.md` 显式推荐某个业务 Capability：

```text
多个可见 Tool 名称/语义非常接近
模型容易选择错误但这种区别属于领域知识
必须强调“用 A 类事实，不要用 B 类事实代替”
```

即便点名，也只写**模型可见的业务语义 Capability**，不写底层 ObservationRef、ObservationBinding 或环境 endpoint。

不应放进 `SKILL.md` 的内容包括：

- Provider 实现和映射；
- 部署地址、凭据；
- raw `ObservationRef`；
- ObservationBinding；
- ObservationSource endpoint / transport；
- Runtime 状态机；
- Runtime Tool eligibility 规则；
- 资格验证状态；
- Benchmark 评分规则；
- 迁移历史；
- 大段系统架构教程。

这些内容属于各自的实现仓或工程文档，不属于模型上下文。

### 3.1 Skill 语义不等于 Tool 授权

`SKILL.md` 负责 epistemic/domain guidance：

```text
what must be known
what must not be guessed
which inference is invalid
```

真正的 ConnectionAgent Tool 可见上限由 Runtime/Harness 解析：

```text
Runtime Capability Catalog
  + selected Skill/Artifact
  + SkillContract allowedResources
  + Context / Template / AgentProfile / Environment / policy
  -> Runtime Resolved CA Toolset
```

Host / `ca-mcp` 只能机械映射和进一步收缩，不能因为 Skill prose 或 Goal 文本扩大 Tool 权限。

如果某个语义上合适的 read-only Capability 在当前 AgentInstance 中不可见，模型必须按 unavailable 处理，不能绕过 Runtime/`ca-mcp` 直接调用 Sandbox、Service Fabric 或 Observation API。

## 4. Rule / Procedure / Predicate 的长期关系

Rule 新设计已经冻结为**设计基线**，详细说明见 `ca-skill-toolchain/docs/rule-authoring-and-case-lineage.md`。

核心关系：

```text
Rule
  = 什么必须成立 / 什么禁止发生

Procedure
  = 受治理流程怎样执行

Predicate
  = 如何基于 Observation / Evidence 判断 PASS / FAIL / UNKNOWN

Qualification Case
  = 如何证明 Skill Artifact 具备资格

Benchmark Case
  = 如何独立评价 Model / Agent / Harness / System
```

它们不合并成一个对象。

例如：

```text
Rule:
  OUTCOME_UNKNOWN 后不得 blind retry

Procedure:
  mutation OUTCOME_UNKNOWN -> reconcile

Predicate / Evidence:
  判断目标状态或 reconcile 结果
```

Procedure 可以保障 Rule，但 Procedure node 不是 Rule identity；Predicate 可以判断某些 Rule 所需事实，但 Predicate 也不是规范正文。

### 4.1 一套 CA Authoring Language Core

后续 Rule 如果正式实现，不应再创造一套独立 DSL。长期目标是 Procedure、Rule、Predicate、Case 尽量复用相同的基础语法原语，例如：

```text
ref
from / value
when
expression
verify
path / op / value
for   # 仅允许需要迭代的 artifact
```

但每种 Artifact 是受限子语言：

```text
Procedure
  可以 call / tool / reconcile / on / terminal

Rule
  只表达 when / verify / appliesTo / violation / severity
  不执行 mutation，不拥有流程路由

Predicate
  只定义 observations / freshness / evaluator

Case
  只定义 challenge / fixture / evidence / expectation
```

原则是：

> **共享基础语法，不共享执行权限。**

### 4.2 Rule ID 与 Violation Code 分离

未来 Rule 使用稳定的具体规范身份，例如：

```text
5gc-file-transfer.urgency.explicit-only
execution.outcome-unknown.no-blind-retry
```

评测侧的跨 Skill 违规类别则可以是：

```text
PARAMETER_FABRICATION
BLIND_RETRY_AFTER_UNKNOWN
INVENTED_RUNTIME_STATE
```

具体 Rule 与统计用 Violation family 不使用同一个 ID 空间。

### 4.3 当前不要提前迁移

当前 Toolchain 还没有：

```text
SkillRuleSet schema
rules.yaml package support
SkillTestCase.ruleRefs
Rule compile/artifact
```

因此现在仍按本文后续章节中的现行语法编写。正式迁移会先以 `5gc-file-transfer` 做 reference migration，再决定 machine contract。

## 5. `assurance/` 三个文件分别负责什么

对于可执行 Skill：

| 文件 | 职责 |
| --- | --- |
| `contract.yaml` | 声明目标、允许使用的资源、前置条件、可满足要求、后置条件以及规划约束 |
| `procedure.yaml` | 声明确定性的流程结构、数据绑定和结果路由 |
| `predicates.yaml` | 声明需要观察什么，以及如何基于已获取 Evidence 做确定性判断 |

其中 `contract.yaml` 的 `allowedResources.capabilities` 还有一个重要作用：它是 Runtime/Harness 计算当前 Skill 的 ConnectionAgent Tool eligibility 时的**资源上限输入之一**。

必须保持：

```text
allowedResources.capabilities
  = Skill 可以使用的 Capability universe / upper bound input

Runtime Resolved CA Toolset
  = 当前 resolved Agent/Skill/Context/Environment 最多允许模型看到的 CA Capability 子集
```

所以 `allowedResources.capabilities`：

- 可以包含模型规划可能需要的 read-only / inspect Capability；
- 也可以包含 deterministic Procedure 内部使用、但不需要直接暴露给模型的 Capability；
- 不是 MCP Tool catalog；
- 不等于最终 model-visible Toolset；
- 不能绕过 Environment / policy / Runtime admission。

对应的 Platform 权威 Schema：

| Skill 源码 | Platform Schema |
| --- | --- |
| `assurance/contract.yaml` | `schemas/v1alpha1/skill-contract.schema.yaml` |
| `assurance/procedure.yaml` | `schemas/v1alpha1/procedure-source.schema.yaml` |
| `assurance/predicates.yaml` | `schemas/v1alpha1/predicate-set.schema.yaml` |
| `cases/<case>/case.yaml` | `schemas/v1alpha1/skill-test-case.schema.yaml` |
| Python 脚本元信息 | `schemas/v1alpha1/script-tool-metadata.schema.yaml` |

当前 `procedure.yaml` 应以 `procedure-source.schema.yaml` 为准，使用对象形式的 Procedure vNext：

```text
procedures
  -> <procedure>
       -> start
       -> nodes
```

不要从历史 `procedure-set.schema.yaml` 推导当前 Skill 源码写法。

详细节点、Binding、Predicate、脚本和用例示例统一放在：

```text
.agents/skills/create-connectionagent-skill/references/authoring-syntax.md
```

## 6. Observation、Evidence、Agent 查询与 Predicate

这些概念不要混在一起理解。

### 6.1 Agent 查询

模型需要当前事实来决定下一步时，应在 Runtime Resolved CA Toolset 中自主选择合适的 read-only Capability。

正常链路：

```text
Skill/domain constraints
  -> what must be known / what must not be inferred

Runtime/Harness
  -> resolves allowed read-only Capabilities

Agent
  -> chooses one visible read-only Tool
  -> ca-mcp
  -> Runtime read-only Capability
  -> Runtime Observation acquisition / Provider read path
  -> trusted fact
  -> Agent planning
```

模型不需要知道 raw ObservationRef、ObservationBinding、Sandbox Observation API 或 Service Fabric internal stream。

Skill 默认不需要指定具体 Tool 名；只有真实领域歧义时才点名。

### 6.2 Runtime Assurance

Runtime 根据 Predicate 声明获取所需 Observation，并形成可供判断的 Evidence。随后 Evidence Gate 检查所需数据是否存在、是否新鲜、是否可用。

```text
Procedure / precondition / postcondition
  -> Predicate
  -> required Observation
  -> Runtime Observation acquisition
  -> Evidence
  -> PASS / FAIL / UNKNOWN
```

如果必要 Evidence 缺失、过期或不可用，应得到 `UNKNOWN`，而不是把“没有证据”误判成业务 `FAIL`。

### 6.3 共用事实基础设施，不共用 verdict authority

Agent read-only Capability 与 Runtime Assurance 可以共用同一 ObservationSource、binding、normalization、provenance 以及满足 freshness 条件的 observation cache。

但必须保持：

```text
Agent read result
  = planning input

Predicate result
  = assurance verdict authority
```

模型刚查询过状态，不代表 postcondition 自动 PASS；Runtime Assurance 也不依赖模型必须先查询。

Observation 的事实类型仍按来源/语义区分，例如 Network Observation 与 Environment Observation；不要再引入 `Planning Observation`、`Agent Observation Projection` 等并列类型。

### 6.4 Predicate evaluator

判断器建议：

- 简单、可审计的确定性判断优先使用 CEL；
- 复杂但仍然确定性的领域判断使用受治理的 Predicate 脚本。

Predicate 脚本只能判断已经提供的数据，不能主动调用 Provider、MCP、网络服务，也不能自行重新获取 Evidence。

未来 Rule 表达式也应优先复用这套确定性表达式方向，不为 Rule 再发明一套表达式语言。

## 7. 资格验证用例怎么写

Skill 内的用例属于源码包的资格验证资产，不是 Benchmark 评测用例。

每个用例一个文件：

```text
cases/<case>/case.yaml
```

用例数量不需要固定，应覆盖该 Skill 真正存在的语义义务。常见覆盖包括：

- 正常成功；
- 操作失败或被拒绝；
- Evidence `UNKNOWN`；
- 变更操作出现 `OUTCOME_UNKNOWN` 后进行调和；
- 规划与预算限制；
- 后置条件独立验证失败；
- 当规划依赖当前状态时，模型是否能在允许的 read-only Toolset 中自主找到合适 Capability，而不是猜测状态；
- 如果存在领域歧义，Skill 的语义约束是否足以避免模型用错误事实替代正确事实。

不要把 mock / fixture 返回值直接当成业务成功证明。最终结果仍应由后置条件或独立 Evidence 证明。

`SkillTestCase` 也不能替代 `BenchmarkCase`。Benchmark 的黑盒裁决不能直接依赖 Skill 内部预期路径。

未来两者会通过稳定 `ruleRefs` 建立 lineage，但仍保持：

```text
SkillTestCase
  = package/artifact qualification
  = fixture-driven

BenchmarkCase
  = independent evaluation question
  = held-out variants + independent evidence
```

不能把 Qualification 用例原样复制成正式 Benchmark 题目，否则模型可能只是在复现已经暴露的例题，而不是泛化遵从 Rule。

## 8. 优先参考真实 Skill，不再维护第二套教学例子

新增 Skill 时，优先找最接近的正式包参考：

| 需求 | 参考 Skill |
| --- | --- |
| 完整但较紧凑的端到端流程 | `query-weather-for-ue` |
| 变更操作、`OUTCOME_UNKNOWN` 与调和 | `ue-registration` |
| 可满足要求与后置条件 | `ensure-session-qos` |
| 截止时间与本地计算 | `download-object-by-deadline` |
| 非执行型路由策略 | `5gc-intent` |

真实 Skill 会跟随编译器持续验证，比额外维护一套教学包更可靠。

Rule/Case 新模型落地前，`5gc-file-transfer` 将作为 reference migration 对象，不要以尚未完成的 reference 设计替代当前正式包语法。

## 9. 推荐编写流程

新增或结构性修改 Skill 时，按下面顺序进行：

1. 阅读仓库根目录 `AGENTS.md`。
2. 判断这是可执行 Skill、路由策略 / 模型上下文，还是 Runtime Capability。
3. 找 1～2 个最接近的正式 Skill 参考。
4. 优先复用已有 Registry 中的 Capability、Predicate 和 Schema。
5. 如果模型规划可能需要当前状态，确认现有 Registry 中是否已有合适的 read-only Capability，并把它纳入正确的 `allowedResources.capabilities` 资源边界；不要为了提示模型而把底层 Observation wiring 写进 `SKILL.md`。
6. 只在领域语义确实容易误选时，在 `SKILL.md` 补充“应该依赖哪类事实/Capability”的指导。
7. 需要改 `assurance/`、脚本或用例时，按需查看 `references/authoring-syntax.md` 对应章节。
8. 单独编译当前 Skill：

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

   默认从兄弟目录 `../ca-skill-toolchain` 查找 Toolchain。如需指定路径，设置：

   ```bash
   export CA_SKILL_TOOLCHAIN_ROOT=/path/to/ca-skill-toolchain
   ```

   历史环境变量 `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` 仍作为 compatibility alias 保留。

9. 提交前运行完整仓库验证：

   ```bash
   make verify
   ```

10. 如目标是更高等级资格验证或生产环境准入，再进入 Platform / Runtime / Sandbox 对应流程。

编译通过或本地预检通过，不等于已经通过生产环境资格验证。

## 10. 仓库之间的边界

可以简单记成：

```text
ca-skills
  编写指南 + 官方 Skill / Rule 源码 authority
  Skill resource boundary + epistemic/domain guidance
  # Rule machine source 在 Schema 落地后启用

ca-skill-toolchain
  Schema + 编译器 + 资格验证

ca-runtime / Harness
  准入 + ConnectionAgent Tool eligibility + 绑定 + 确定性执行 + Observation/Evidence/Predicate authority

ca-mcp
  Runtime-authorized Capability -> Agent MCP Tool 的机械适配

Agent Host
  注册模型可见 Tool；对 CA Tool 只能执行 Runtime Resolved CA Toolset 或进一步收缩

ca-benchmarks / ca-benchmark-engine
  BenchmarkCase + held-out evaluation + assessment
```

当某个真实场景暂时表达不出来时，不要首先扩展 Skill 语法。先确认缺口究竟来自：

- 缺少合适的 read-only Capability；
- Skill `allowedResources.capabilities` 资源边界；
- Runtime Tool eligibility resolution；
- ProviderBinding；
- ObservationBinding / ObservationSource；
- Runtime 能力；
- 资格验证；
- Benchmark / Judge；
- Sandbox / 集成环境。

只有确认现有语言本身确实无法表达必要语义时，才考虑修改 Skill 语言。
