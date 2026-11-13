# ConnectionAgent Skill Language Specification（CA-SL）

**中文名称：** ConnectionAgent Skill 语言规范  
**简称：** CA-SL  
**目标版本：** vNext / API v1alpha2  
**状态：** PUBLIC DESIGN REVIEW — NOT FROZEN  
**规范所有者：** odango-chan/ca-skills  
**消费者：** Skill 作者、Skill Studio、ca-skill-compiler、Agent Host / Runtime、Tool Owner、Schema Owner、语言服务和第三方评审者  
**更新日期：** 2026-11-13

> 本文是 CA-SL vNext 的综合规范评审稿，也是本仓库唯一的语言语义权威。它覆盖背景、设计原则、术语、架构、源码结构、YAML 语法、静态语义、运行语义、Tool / Observation / Evidence、Schema 所有权、异常处理、PDU Session 示例、工具链要求和 FAQ。其他文档可以补充实现细节，但不得另行定义或覆盖语言语义。
>
> MUST、MUST NOT、REQUIRED、SHOULD、SHOULD NOT、MAY、OPTIONAL 等关键字遵循 RFC 2119 / RFC 8174。中文“必须、不得、应当、不建议、可以”具有相同规范效力。

---

# 第一部分：背景与目标

## 1. 为什么需要 CA-SL

ConnectionAgent Skill 不是一段 Prompt，也不是一组供模型自由挑选的工具说明。它描述 Agent 如何在明确业务目标、输入、上下文和授权范围内，执行确定性步骤、验证事实、处理不确定结果并给出可审计结论。

以 5G PDU Session Establishment 为例，Agent 不仅要知道如何调用 UDM、PCF、AMF、SMF，还必须知道：

- 请求属于哪个 UE、PDU Session、PTI 和生命周期；
- 输入来自哪个权威来源，是否仍然有效；
- 哪个 Tool 可以执行什么动作，输入输出由谁定义；
- 某次调用是 READ 还是 MUTATION，是否被授权；
- 某个状态是 Operation Result、Observation Result，还是 Host 捕获的 Context；
- Mutation 已提交但响应丢失时，如何避免重复创建；
- Predicate 为什么可以 PASS，支持它的 Evidence 是什么；
- Evidence 缺失、过期、冲突或无法查询时，为什么必须 UNKNOWN；
- 多个 UE、多个 Session 和多个 Invocation 如何保持隔离。

CA-SL 将这些边界变成可阅读、可静态检查、可链接、可编辑、可执行和可审计的契约。

## 2. 设计目标

CA-SL MUST 满足：

1. 业务目标清晰：Skill 描述业务目标和完成条件，不把网元实现细节伪装成业务语义。
2. 执行确定：Procedure 明确表达步骤、依赖、分支、失败处理和终态，不依赖隐式前序节点或模型临场猜测。
3. 输入有来源：每个输入来自 Skill 自有 Schema、Owner Schema、Operation Result、Context Projection 或显式 Observation Query。
4. 契约归属唯一：Schema 由真正拥有数据或接口的 Owner 发布；消费者不得复制并重新定义外部结构。
5. 权限可证明：Skill 授予 Capability；Procedure 调用精确 callable；部署侧 CapabilityContracts 定义 callable 归属和 Effect。
6. 观察与操作分离：Operation Result 与 Observation Result 保持不同语义；Observation 是受治理的只读查询能力。
7. Evidence 独立：Evidence 证明业务值的来源、主体、时间和相关性，不是业务 Payload 的替代品。
8. 不确定性显式：PASS、FAIL、UNKNOWN 不得混为一谈；Mutation 结果不确定时必须 Reconcile 原操作。
9. 运行时边界明确：Script 只做确定性本地计算；Tool 负责外部交互；Host / Runtime 负责授权、隔离、Evidence 和执行治理。
10. 工具链同源：Compiler、LSP、Skill Studio 和 Runtime 消费同一套语言语义。
11. 可演进：语言版本、Schema 身份和 Owner 契约版本明确；破坏性变化不通过静默兼容掩盖。
12. 可审查：规范可以脱离实现代码独立阅读和评审。

## 3. 非目标

CA-SL 不是通用编程语言、BPMN 替代品、Prompt DSL、Tool / MCP / HTTP API 重新定义、Package Manager、Dependency Resolver、数据库、记忆系统、Python 执行环境、实时网络状态真相来源、Qualification / Case Runner，也不是 3GPP 协议字段的第二套定义。

CA-SL 描述 Agent 如何在 Owner 已发布契约上进行确定性编排，不取代 3GPP、OpenAPI、AsyncAPI、Provider API 或网元内部协议。

## 4. 符合性角色

| 角色 | 责任 |
|---|---|
| Skill Package | 遵守源码、身份、引用、绑定和授权规则 |
| Compiler | 解析、链接、校验、生成诊断和规定的派生产物 |
| Skill Studio | 编辑、依赖快照、语义导航和诊断体验 |
| Tool Owner | 发布真实、完整、版本化 ToolCatalog 与 Input/Output Schema |
| Observation Owner | 发布查询身份、QueryContext、输出、来源、范围和 Evidence 保证 |
| Capability Owner / Deployment | 发布可信 CapabilityContracts，定义授权边界 |
| Host / Runtime | 授权、Effect、Scope、Evidence、Deadline、Cancellation 和隔离 |
| Script | 只做确定性本地计算，不越过 Tool / Runtime 边界 |

Build 成功不等于 Runtime READY；Runtime READY 不等于执行成功；Skill 执行成功也不自动等于真实 5GC 验收成功。

---

# 第二部分：概念模型与术语

## 5. 五层模型

1. **Skill 层：** 业务目标、输入契约、Context Projection、Capability Grants、最终条件。
2. **Procedure 层：** 确定性流程图、Operation / Observation 调用、Script、Predicate、分支和恢复。
3. **Tool / Observation 层：** Owner 发布的可调用契约、输入输出 Schema、Effect 和数据来源。
4. **Capability 层：** 部署授权边界，将精确 callable 归入授权单元。
5. **Host / Runtime 层：** 执行隔离、调用、Evidence、Correlation、Freshness、Deadline、Cancellation 和最终状态。

~~~text
Skill
 ├── SkillContract
 ├── Procedure
 │    ├── Operation calls
 │    ├── Observation queries
 │    ├── Scripts
 │    ├── Predicate evaluations
 │    ├── Reconciliation
 │    └── Explicit routes
 ├── PredicateSet / Schemas / Cases / References
ToolCatalog ── Operations + Observation query contracts
Owner Schemas ── authoritative data structures
CapabilityContracts ── callable → Capability + Effect
Host / Runtime ── admission, execution, correlation, Evidence
~~~

## 6. 术语

### 6.1 Skill / Skill Package

Skill 是具有明确业务目标、输入契约、授权范围和执行入口的可复用业务能力包。Skill 不是 Tool；一个 Skill 可以调用多个 Tool，也可以被 Agent Router 选择。

标准 Package：

~~~text
skills/<skill-name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/<case-name>/case.yaml
├── schemas/
├── scripts/
└── references/
~~~

| 资产 | 职责 |
|---|---|
| SKILL.md | 面向 Agent 的业务指导，不是第二份执行图 |
| contract.yaml | SkillContract |
| procedure.yaml | Procedure 源码 |
| predicates.yaml | PredicateSet |
| cases/ | 业务场景和预期语义义务 |
| schemas/ | 仅真正由 Skill 拥有的 Schema |
| scripts/ | Skill 自有确定性 Python |
| references/ | 可选知识资料，不是执行契约或 Evidence |

vNext 不使用 package-local lib/ 存放导入契约，也不使用 output/ 作为 Compiler 输入。导入契约由 Studio / 调用方通过 BuildRequest 的 DependencySnapshot 提供。

### 6.2 SkillContract、Goal、Request、Invocation

- **SkillContract：** Skill 根契约，声明身份、目标、入口、输入、Context Projection、Capability 授权上界和最终条件。
- **Goal：** Skill 希望达成的业务目标，不等于某个 Operation 成功。
- **Request：** 调用方为本次执行提供的业务请求，由 Skill 自有 Request Schema 约束；Request 本身不证明网络状态。
- **Invocation：** 一次 Skill 独立执行实例。每次 Invocation MUST 有独立运行身份和隔离上下文。不得因为 UE 相同而共享未声明的可变状态。

### 6.3 Context、Subject、Facts、Ingress

- **Context：** Host 在 Invocation 中向 Skill 显式开放、经过授权和 Schema 约束的上下文投影，不是任意全局对象。
- **Subject：** 本次业务执行的主体，5GC 场景通常是 UE 的稳定引用。Schema 由 Host Owner 发布。
- **Facts：** Host / Owner 已知、可引用的事实或事实句柄集合。句柄本身不等于事实成立。
- **Ingress：** 本次 Invocation 接收的原始或规范化请求入口上下文，例如被 Host 接纳的网络消息、请求类型、序列号和关联身份。Skill 不得伪造 Ingress。

### 6.4 Procedure、Node、Step

Procedure 是有向、确定性的执行图，定义入口、节点、输入、动作、路由、前置后置条件、恢复和终态。

Node 是主流程中的业务显著步骤。Step 是 Node 内部有序的前置或后置步骤。局部计算不必为每个小动作增加主流程 Node。

### 6.5 Tool 与 Operation

- **Tool：** 由 Owner 注册、实现并发布契约的外部能力单元，可由 HTTP Adapter、MCP、内建集成或其他受治理实现提供。Tool 是实现和契约发布单元，不是 Skill 授权身份。
- **Operation：** Tool 提供的精确可调用业务接口，声明唯一 ID、Effect、Input Schema、Output Schema，以及对 Mutation 可选的 Reconcile Output Schema。Operation Result 描述这一次调用返回了什么。

### 6.6 Fact、Observation Query、Observation Result

必须区分：

- **Fact：** 关于业务、环境或执行状态的命题，例如“目标 UE 的指定 PDU Session 当前拥有已建立的 N4 资源”。
- **Observation Query：** 向权威事实 Owner 查询状态的独立只读 Tool 接口，是 Tool 体系中的特殊 callable，Effect 必须为 READ。
- **Observation Result：** Observation Query 返回的、带来源、Scope、时间和相关性语义的规范化事实表示。

Observation Query MUST 由真正拥有或有权查询事实的 Owner 发布；必须有精确身份、QueryContext / Input Schema、Output Schema、READ Effect、权威来源、Scope、Temporal / Freshness、Correlation 和 Evidence 保证；必须通过 CapabilityContracts 授权和 Runtime Admission。

Observation Query MUST NOT 在 Predicate 内部隐式触发；不得强制与每个 Mutation 一对一配对；不得用于轮询刚调用的 Operation 的内部异步完成；不得仅因返回 JSON 就被视为可信事实。

一个 Tool 可以暴露多个 Observation Query。不存在 Mutation Operation 必须配套一个 Observation Query 的一对一要求。

### 6.7 Operation Result 与 Observation Result

| 维度 | Operation Result | Observation Result |
|---|---|---|
| 回答的问题 | 这一次调用返回了什么？ | Owner 对某个事实的查询结果是什么？ |
| 关联对象 | 一次 Operation Invocation | 明确查询 Scope 和查询时点 |
| 典型来源 | Tool 调用 | Observation Tool Query |
| 是否必须额外查询 | 否 | 仅在需要独立权威上下文时 |
| 是否证明外部状态 | 取决于 Operation 契约和 Evidence | 取决于 Observation Owner 的权威和 Evidence |

若前序 Operation Result 已提供精确业务值，且 Evidence 足以证明来源、Scope、Correlation 和 Freshness，MUST 直接复用，不得为了“有 Observation”重复查询。

Mutation 成功响应也不自动证明网络状态达到目标。若 Mutation Result 仅证明请求已提交，仍需要最终结果或独立 Observation。

### 6.8 Evidence

Evidence 是对业务值或事实的来源、完整性、Scope、时间和相关性支持。Evidence 不是业务 Payload，不是随意传入的布尔值，也不是“有一个 ref 就代表 PASS”。

Evidence 至少需要表达或可由可信 Owner / Host 关联出：

| 维度 | 含义 |
|---|---|
| Producer / Owner | 谁产生或权威发布该事实 |
| Producer Contract | 哪个版本化 Operation / Observation 契约 |
| Producer Invocation | 哪一次调用产生该值 |
| Record / Artifact | 对应记录、资源、事件或产物引用 |
| Subject Scope | 属于哪个业务主体 |
| Resource Scope | 属于哪个 UE / Session / PSI / 资源实例 |
| Lifecycle / Generation | 属于哪个生命周期或资源代次 |
| Correlation | 对应哪次请求、事务或协议交互 |
| Temporal | 事件时间、Owner 观察时间、Host 接收时间 |
| Freshness | 有效时间窗、版本或新鲜度保证 |
| Integrity | 可选 Digest、签名或 Owner 完整性保证 |
| Schema Identity | 规范化 Payload Schema 身份 |

不是所有 Evidence 都必须平铺成一个 JSON 对象；Owner 可以使用内部结构，但对外契约 MUST 允许 Host 验证当前事实所需维度。

eventTime、observedAt 和 receivedAt 不得混为一个时间戳。

Payload 是 Predicate 判断的业务值；Evidence 是 Host 判断该值是否可信的依据；Evidence refs 是可信记录引用。Skill Script 不得创建或扩大 Evidence。

### 6.9 Predicate、Capability、Effect、Reconcile

- **Predicate：** 纯、可重复、无副作用的确定性计算 / 判断函数，声明有序类型参数，使用 CEL 或受限 Python Script 实现，返回 PASS / FAIL / UNKNOWN。它由 Procedure 的 Precondition 或 Postcondition 节点调用，不是独立 Procedure Node。
- **Capability：** 部署侧授权分组和资源边界，不是 callable，也不是 Operation 别名。一个 Capability 可以包含多个 Operation 和 Observation Query。Skill 只声明 Capability Grant。
- **Effect：** 初始支持 READ 和 MUTATION。READ 仍需要授权、Scope 和审计。
- **Reconcile：** 对已经发起但结果不确定的原始 Mutation 进行调和。它是 Operation 的受约束执行模式，不是独立业务节点类型；必须针对原始身份、Operation Ref、Correlation 和 Scope，不得偷偷创建新 Mutation。

### 6.10 Script、Case、Reference

- **Script：** Skill Package 自有确定性 Python，仅作为 Predicate 的 evaluator 实现，不是独立 Procedure Node，也不是 Tool / Operation / Capability。
- **Case：** 业务场景和预期语义义务声明，不是执行器，不证明真实运行通过。
- **Reference：** 给 Agent 阅读的补充知识，不是 Tool Schema、Evidence 或自动 Runtime 输入。

---

# 第三部分：架构边界与契约所有权

## 7. 唯一责任边界

| 事项 | Owner | 不得由谁代替 |
|---|---|---|
| Skill 业务目标和流程源 | ca-skills / Skill 作者 | Host 不得重写业务决策 |
| Skill 源码语义 | 本规范 | Compiler 不得自行发明语义 |
| Request Schema | Skill Owner | Host 不得复制定义 |
| Tool Input / Output Schema | Tool Owner | Skill 不得维护影子 Schema |
| Observation Query Schema | Observation Owner | Predicate 不得定义查询 Payload |
| Subject / Facts / Ingress | Host / Context Owner | Skill 不得伪造可信上下文 |
| Evidence 记录和校验 | Evidence Producer + Host | Script 不得制造可信 Evidence |
| Capability 成员和授权 | Deployment Capability Owner | Skill 不得扩大授权 |
| 依赖获取和快照 | Skill Studio / 调用方 | Compiler 不得联网获取 |
| 静态解析和链接 | Compiler | Runtime 不得静默修补源码 |
| 外部副作用 | Tool / Provider / Adapter | Script 不得直接访问外部系统 |
| Deadline / Cancellation | Host / Runtime | Skill 不得定义任意轮询循环 |
| 真实网络状态 | 对应网元 / Owner | Skill 本地变量不是真相来源 |

## 8. Schema 所有权和身份

Skill 可以拥有公共 Request Schema 和真正属于 Skill 的业务结构，放在 schemas/。

Tool Owner 必须发布 callable 的 Input、Output，以及 Mutation 所需的 Reconcile Output Schema。下游需要静态访问嵌套字段时，Owner 必须提供完整结构，不得长期用宽泛 object 掩盖缺失字段。

Observation Owner 发布 QueryContext / Input 和规范化 Output Schema。不得在 Skill Package 或平行 Observation Registry 中复制第二份。

Host / Context Owner 发布 Subject、Facts、Ingress 等 Projection Schema。SkillContract 声明可使用哪些 Projection，但它们不会自动注入 Procedure 或 Operation 输入。

Script 输入和输出：
- Python Script 仅作为 Predicate 的确定性 evaluator，不是独立 Procedure Node；
- Predicate Script 输入类型由 Predicate.parameters 派生，Host 附加只读 Evidence refs；
- Predicate Script 的返回类型必须是 PASS、FAIL、UNKNOWN 三态之一；
- 作者不得维护重复 Script Input Schema；
- Compiler 不得执行 Python 函数体猜测类型。

必须区分物理路径、Schema 身份和 Dependency Alias。外部 Schema 使用：

~~~yaml
type: host-context::urn:connectionagent:5gc:skill-context:subject:v1
~~~

host-context 是依赖别名，后半部分是 Owner 发布的精确 Schema $id。Skill 自有 Schema 使用包内路径：

~~~yaml
type: schemas/establishment-request.schema.yaml
~~~

文件路径不是跨包公共身份。Compiler 必须验证引用指向真实 Schema 身份，不得通过文件名猜测。

## 9. ToolCatalog 和 CapabilityContracts

### 9.1 ToolCatalog

ToolCatalog 是 Tool Owner 发布的 callable 契约集合。vNext 要求同一 ToolCatalog 和依赖快照能够容纳 Operation 与 Observation Query 两种 callable。两者是不同类型，但共享精确导出身份、Owner、Schema、Effect、依赖解析、Capability 授权和 Runtime Admission。

### 9.2 Observation 在 ToolCatalog 中的候选表达

以下是候选结构，不是已冻结的现有文件格式：

~~~yaml
apiVersion: connectionagent.io/toolcatalog/v1alpha2
kind: ToolCatalog
metadata:
  name: smf-session-state
  owner: smf-owner
spec:
  contracts:
    - kind: operation
      id: smf.session.create
      adapter: smf-http
      effect: MUTATION
      inputSchema:
        $ref: urn:example:smf:create-session-input:v1
      outputSchema:
        $ref: urn:example:smf:create-session-result:v1
    - kind: observation
      id: smf.session.n4_resources
      adapter: smf-state-query
      effect: READ
      queryContextSchema:
        $ref: urn:example:smf:n4-query-context:v1
      outputSchema:
        $ref: urn:example:smf:n4-observation-result:v1
      guarantees:
        authority: smf-session-owner
        scope: [subject, pduSession, lifecycle, sessionInstance]
        temporal:
          eventTime: required
          observedAt: required
        freshness:
          policy: owner-declared
        evidence:
          correlation: required
          producerInvocation: required
~~~

kind 区分 operation 和 observation；id 在同一导出身份域中唯一；QueryContext Schema 不是 Operation Input Schema 的任意别名；Observation Output Schema 是 Owner 对外承诺的规范化结果；guarantees 是契约声明，Runtime 必须验证实际 Evidence；adapter 是 Owner 内部实现绑定，不是 Skill 源码身份。

不得通过通用 observation.read 和任意字符串 selector 暴露任意内部数据。最终字段、版本和兼容策略必须由 Tool Owner、Compiler 和 Runtime 评审，并通过正负例 Fixture 后冻结。

### 9.3 CapabilityContracts

CapabilityContracts 是部署侧可信输入，独立于普通 DependencySnapshot。候选形式：

~~~yaml
apiVersion: connectionagent.io/capability-contracts/v1alpha2
kind: CapabilityContracts
metadata:
  name: 5gc-createdsession
spec:
  capabilities:
    - id: provider-5gc.session-mutation
      owner: deployment
      callables:
        - owner: provider-5gc
          id: sbi.udm.sdm_subscription.create
          kind: operation
          effect: MUTATION
        - owner: smf-owner
          id: smf.session.n4_resources
          kind: observation
          effect: READ
~~~

CapabilityContracts 使用稳定 Owner 身份 + 精确 callable ID + kind 标识成员，不得使用 BuildRequest 中临时的 Dependency Alias。Compiler 先通过 Skill 源码中的 Alias 找到 ToolCatalog，再以其 metadata.owner 和 callable 身份链接到 CapabilityContracts。每个被调用 callable 必须且只能映射到一个 Capability；Effect 必须与 ToolCatalog 一致；Skill 只能 grant Capability ID；缺失、重复或 Effect 不一致必须 fail-closed；Runtime 必须重新执行授权和 Effect Admission。该 YAML 是候选表达，必须与部署侧真实 CapabilityContracts 结构统一。

---

# 第四部分：源文件与 YAML 语法

## 10. 版本和文件

目标根对象：

~~~yaml
apiVersion: connectionagent.io/v1alpha2
kind: SkillContract
~~~

vNext 是破坏性版本。Compiler MUST NOT 静默把 v0.2 字段、旧路径或旧隐式输入模型转换为 vNext 语义。

当前仓库中的可执行 5GC Skill 仍有 v0.2 形态。本文示例说明目标语言，不代表旧文件已迁移或当前 Compiler 已支持。

## 10.1 YAML 语法子集与结构文法

CA-SL 使用 YAML 1.2 表达源文件。YAML 是序列化格式，不是完整语言语义。Compiler MUST 使用安全解析器，并拒绝重复 Key、未知语义字段、非预期根类型、自定义 Tag、循环 Alias 和无法确定解释的标量。

规范性结构文法（抽象 EBNF；字段约束由对应对象 Schema 和本规范语义规则补充）：

~~~ebnf
SkillDocument       = SkillContract ;
ProcedureDocument   = ProcedureSet ;
PredicateDocument   = PredicateSet ;

ProcedureSet        = "procedures", ProcedureMap ;
Procedure           = [ProcedureInputs], StartNode, NodeMap ;
Node                = ExactlyOne(NodeAction), [OperationArguments], [Routes] ;
NodeAction          = Precondition | Operation | Observation |
                      Postcondition | Terminal ;

Precondition        = "precondition", PredicateInvocation ;
Postcondition       = "postcondition", PredicateInvocation ;
PredicateInvocation = "predicate", PredicateIdentity,
                      "arguments", ArgumentList ;

Operation           = "operation", OperationTarget ;
OperationTarget     = CallableIdentity | ReconcileTarget ;
Observation         = "observation", CallableIdentity ;
OperationArguments  = "arguments", ArgumentMap ;
ReconcileTarget     = "reconcile", OriginalMutationNode ;
Terminal            = "terminal", TerminalStatus ;
Routes              = "on", RouteMap ;

ProcedureInputs     = "inputs", SourceMap ;
SourceMap           = Map<Identifier, SourcePath> ;
ArgumentMap         = Map<Identifier, ArgumentExpression> ;
ArgumentList        = OrderedList<ArgumentExpression> ;
ArgumentExpression = SourcePath | YAMLScalarLiteral ;

PredicateDocument   = "predicates", PredicateMap ;
Predicate           = OrderedParameters, Evaluator ;
Evaluator           = CELExpression | PredicateScriptEvaluator ;
~~~

该文法规定 Procedure 的五种结构节点：Precondition、Operation、Observation、Postcondition 和 Terminal。Terminal 是流程终止声明，不是第五种业务动作。Predicate 是独立定义的确定性逻辑，不是 Procedure 节点类型；它由 Precondition / Postcondition 引用。Operation 与 Observation 是不同类型的 Tool callable。

### YAML 解析规则

- MUST 按 YAML 1.2 规则解析；对影响语义的标量不得依赖 YAML 1.1 隐式类型转换。
- MUST 拒绝同一 Mapping 中的重复 Key。
- MUST 拒绝自定义 Tag、任意对象构造、循环 Alias 和不受支持的 Merge Key。
- 建议将 on 作为字符串键显式加引号，避免不同解析器的历史差异。
- 字段名大小写敏感；导出身份按其 Owner 契约定义的大小写规则处理。
- 未知字段 MUST 报诊断，不得静默忽略。

### 参数表达式

- 在 Procedure.inputs 和 Operation / Observation 的 arguments 映射中，未加引号且符合 SourcePath 文法的标量表示来源引用，例如 `input.ueRef`、`context.subject.ueRef`、`create-session.output.sessionInstanceRef`。
- YAML 原生 Boolean、Number、Null，以及带引号的 String 表示字面量。带引号的 `"input.dnn"` 是字符串常量，不是来源引用。
- vNext 第一版不接受在 arguments 中内联任意对象或数组字面量；复杂值必须来自有 Schema 的输入或 Producer 输出。这样可避免参数对象和来源表达式混淆。
- 不支持隐式同名绑定、自动转发、默认取上一个 Node 输出或从 Context 猜测参数。

### Source Path 与控制流

Source Path 必须解析为静态 Producer 引用。Compiler 必须构建 Procedure 控制流图，并验证 Producer 在所有到达消费者的路径上均已产生。若 Producer 仅在一个互斥分支中产生，则消费者必须位于该分支内，或通过显式控制流合并得到经过验证的值；不得用 null 代替不可用值。

### Procedure Request 与 Context

Procedure 可引用 Skill Invocation 的 Request Projection（例如 `context.request.dnn`），其结构由 SkillContract.inputs.requestSchema 约束。subject、facts、ingress 等 Host Projection 则由 SkillContract.context.projections 精确声明。Request Projection 与 Host Context Projection 是不同来源，不得因为都位于 context 命名空间就混淆 Owner。

## 11. SkillContract

~~~yaml
apiVersion: connectionagent.io/v1alpha2
kind: SkillContract
metadata:
  name: establish-pdu-session
spec:
  skillType: executable
  goal: pdu_session.initial_request_fulfilled
  entryProcedure: ue-requested-pdu-session-establishment
  inputs:
    requestSchema: schemas/establishment-request.schema.yaml
  context:
    projections:
      subject: host-context::urn:connectionagent:5gc:skill-context:subject:v1
      facts: host-context::urn:connectionagent:5gc:skill-context:facts:v1
      ingress: host-context::urn:connectionagent:5gc:skill-context:ingress:v1
    evidenceSchema: host-context::urn:connectionagent:host:predicate-evidence-refs:v1
  allowedResources:
    capabilities:
      - provider-5gc.session-read
      - provider-5gc.session-mutation
      - env-fabric.session-hold
      - ca-agent-host.session-runtime
  postconditions:
    - predicate: createdsession.session.established
      expect: PASS
~~~

| 字段 | 语义 | 约束 |
|---|---|---|
| apiVersion | 语言/API 版本 | 必须精确支持 |
| kind | 根对象类型 | 必须为 SkillContract |
| metadata.name | Skill 身份 | 必须唯一 |
| spec.skillType | Skill 类型 | 当前至少 executable |
| spec.goal | 业务目标标识 | 不等于 Operation |
| spec.entryProcedure | 唯一入口 | 必须链接到 Procedure |
| inputs.requestSchema | 公共 Request Schema | Skill 自有 |
| context.projections | 可访问 Context Projection | Owner Schema 精确引用 |
| context.evidenceSchema | Host Evidence Ref Projection | 不代表 Skill 拥有 Evidence |
| allowedResources.capabilities | 授权上界 | 只能列 Capability ID |
| postconditions | 最终业务验收条件 | 不替代 Node Postconditions |

vNext 不允许直接把 Operation ID 放入授权列表，不允许 localTools，不允许把 Host 内部 dataclass 路径写入 Skill，不允许通过 requiredFacts 名称推断字段结构，也不允许物理 lib 路径作为外部身份。

## 12. Procedure

### 12.1 核心结构

Procedure 是确定性的有向执行图。每个 Node 必须且只能声明一个主动作。vNext 的业务节点只有四种：

1. `precondition`：调用 Predicate 判断执行前置条件；
2. `operation`：调用 ToolCatalog 中的 Operation；
3. `observation`：调用 ToolCatalog 中的只读 Observation Query；
4. `postcondition`：调用 Predicate 判断执行结果。

`terminal` 是显式终态声明，不是业务动作。Predicate、CEL 和 Python Script 都不是独立 Procedure 节点。

~~~yaml
procedures:
  establish:
    inputs:
      ueRef: context.subject.ueRef
      dnn: context.request.dnn
    start: check-registration
    nodes:
      check-registration:
        precondition:
          predicate: createdsession.ue.registered
          arguments:
            - input.ueRef
        'on':
          PASS: read-subscription
          FAIL: failed
          UNKNOWN: unresolved

      read-subscription:
        operation: fivegc-tools::sbi.udm.sm_data.get
        arguments:
          ueRef: input.ueRef
          dnn: input.dnn
        'on':
          SUCCEEDED: check-subscription
          FAILED: failed
          DENIED: failed
          UNKNOWN: unresolved

      check-subscription:
        postcondition:
          predicate: createdsession.udm.subscription_usable
          arguments:
            - read-subscription.output.result
            - input.dnn
        'on':
          PASS: create-subscription
          FAIL: failed
          UNKNOWN: unresolved

      create-subscription:
        operation: fivegc-tools::sbi.udm.sdm_subscription.create
        arguments:
          ueRef: input.ueRef
          subscription: read-subscription.output.result
        'on':
          SUCCEEDED: complete
          NOT_COMMITTED: failed
          OUTCOME_UNKNOWN: reconcile-subscription
          DENIED: failed
          FAILED: failed

      reconcile-subscription:
        operation:
          reconcile: create-subscription
        'on':
          COMMITTED: complete
          NOT_COMMITTED: failed
          UNRESOLVED: unresolved

      complete:
        terminal: SUCCEEDED
      failed:
        terminal: FAILED
      unresolved:
        terminal: UNRESOLVED
~~~

### 12.2 Precondition

Precondition 在受保护的业务动作之前执行 Predicate。它可以检查 Host Context、Request、此前 Operation Result 或 Observation Result。Precondition 不得隐式查询外部系统；若缺少事实，应先通过显式 Observation 获取，再调用 Predicate。

~~~yaml
check-ue-registration:
  precondition:
    predicate: createdsession.ue.registered
    arguments:
      - context.subject.ueRef
  'on':
    PASS: create-session
    FAIL: reject-request
    UNKNOWN: unresolved
~~~

Precondition 的 Predicate 结果必须显式路由 PASS、FAIL 和 UNKNOWN。FAIL 与 UNKNOWN 不得合并。

### 12.3 Operation

Operation 表示一个有副作用或无副作用的业务动作，由 Tool Owner 在 ToolCatalog 中发布精确 callable 身份、Effect、Input / Output Schema 和必要的 Reconcile 契约。

~~~yaml
create-policy:
  operation: fivegc-tools::sbi.pcf.sm_policy.create
  arguments:
    ueRef: input.ueRef
    pduSessionId: input.pduSessionId
    dnn: input.dnn
    sNssai: input.sNssai
  'on':
    SUCCEEDED: verify-policy
    NOT_COMMITTED: failed
    OUTCOME_UNKNOWN: reconcile-policy
    DENIED: failed
    FAILED: failed
~~~

Operation 的 arguments 是具名映射，键必须是 Owner Input Schema 中的字段名；值是显式来源表达式或 YAML 标量字面量。Compiler 按 Schema 检查 Required、类型、Optional、Nullability 和额外字段。Operation 的 Effect 由 ToolCatalog 和 CapabilityContracts 决定，Skill 不得自行声明或覆盖。

### 12.4 Observation

Observation 是 ToolCatalog 中由权威 Owner 发布的只读查询能力。它是可选节点，不是每个 Operation 的必经步骤。

~~~yaml
inspect-policy:
  observation: fivegc-observations::pcf.policy_association.current
  arguments:
    ueRef: input.ueRef
    pduSessionId: input.pduSessionId
  'on':
    SUCCEEDED: verify-policy
    FAILED: failed
    UNKNOWN: unresolved
~~~

Observation 的 arguments 同样是具名映射，并按 Query Input Schema 校验。Observation Query 可以使用前序 Operation Result 作为查询依据，例如：

~~~yaml
inspect-n4-resources:
  observation: fivegc-observations::smf.session.n4_resources
  arguments:
    sessionInstanceRef: create-n4-session.output.sessionInstanceRef
    smfSeid: create-n4-session.output.smfSeid
~~~

这里 Operation Result 只提供查询目标和关联身份；Observation 必须由其权威 Owner 实际执行查询并返回自己的 Result / Evidence，不得把 Operation Result 包装或改名成 Observation Result。

### 12.5 Postcondition

Postcondition 调用 Predicate 判断业务结果是否成立。其参数可以来自 Operation Result、Observation Result、Invocation Context 或多个来源的组合。

~~~yaml
verify-n4-session:
  postcondition:
    predicate: createdsession.n4.established
    arguments:
      - create-n4-session.output
  'on':
    PASS: next-step
    FAIL: failed
    UNKNOWN: unresolved
~~~

如果 Operation Result 已包含满足 Predicate 所需的事实、Scope、Correlation、Freshness 和 Evidence，可以直接作为 Postcondition 输入，不需要 Observation。

### 12.6 Operation Result 充分性原则

**Result Sufficiency Principle（结果充分性原则）：** Procedure MUST 优先复用已有且满足当前判断要求的 Operation Result、Context 和 Evidence。只有当现有信息不足以支持目标 Predicate，或业务规则明确要求独立权威观察时，才执行 Observation。

- Operation Result 已满足业务判断和 Evidence 要求时，不得为了形式上的配对增加重复 Observation。
- Operation Result 只证明请求已接受、未证明目标状态时，应根据业务需要执行 Observation 或等待由 Operation Owner 提供最终完成结果。
- Postcondition 可以同时接收 Operation Result 和 Observation Result，以验证二者之间的一致性。
- Operation 与 Observation 必须保留真实 Producer 身份；不得将 Operation Result 伪装成 Observation Result。
- Observation 的 Freshness 和 Scope 必须满足当前 Predicate 要求；“曾经观察到”不等于“当前仍成立”。

### 12.7 Reconcile

Reconcile 是 Mutation Operation 的受约束调和模式，不是独立业务节点类型。它必须指向本次 Procedure 中一个已执行的原始 Mutation Node：

~~~yaml
reconcile-policy:
  operation:
    reconcile: create-policy
  'on':
    COMMITTED: next-step
    NOT_COMMITTED: safe-to-retry-or-fail
    UNRESOLVED: unresolved
~~~

Runtime 必须使用原始 Mutation 的不可变 Invocation、Operation 身份、输入、Scope 和 Correlation 执行对应 Owner 契约的 Reconcile。Reconcile 不得变成新的 Create / Update 请求，不得接受另一组业务参数来改变原操作目标。Compiler 必须验证目标存在、目标确为 MUTATION、Reconcile 路径可达且引用的是当前 Invocation 的原始操作。

### 12.8 Terminal 与 Applicability

Terminal 声明明确终态，例如 SUCCEEDED、FAILED、UNRESOLVED。不得通过缺失边或最后一个节点自然结束来隐式推断。

Skill Eligibility 属于 Root Routing / Host 准入。无法唯一匹配时不得随机选择或默认执行。Procedure Predicate 负责业务条件，不负责猜测 Skill 身份。完整 Applicability YAML 语法需要与 Root Routing 契约统一冻结；历史 applicability.when 不作为隐式兼容语法。

## 13. Arguments 与数据来源

### 13.1 统一表达

vNext 删除 Procedure Node 上的 `with` / `from` / `value` 包装，统一使用直接表达式：

- Procedure.inputs：具名映射，值为 Source Path；
- Operation.arguments：具名映射，键为 Owner Input Schema 字段，值为来源表达式或标量字面量；
- Observation.arguments：具名映射，键为 Query Input Schema 字段，值为来源表达式或标量字面量；
- Precondition / Postcondition.arguments：有序列表，位置与 Predicate.parameters 严格对应。

~~~yaml
procedures:
  establish:
    inputs:
      ueRef: context.subject.ueRef
      dnn: context.request.dnn
    nodes:
      create-session:
        operation: fivegc-tools::smf.session.create
        arguments:
          ueRef: input.ueRef
          dnn: input.dnn
~~~

### 13.2 参数表达式

- 未加引号且符合 Source Path 语法的标量表示引用，例如 `input.ueRef`、`context.subject.ueRef`、`create-session.output.sessionInstanceRef`。
- YAML 原生 Boolean、Number、Null 和带引号的 String 表示字面量。例如 `phase: "POST_CREATE"` 是字符串常量；`phase: input.phase` 是来源引用。
- vNext 第一版不允许在 arguments 中内联任意对象或数组字面量；复杂对象必须来自一个有 Schema 的 Request、Context 或 Producer Output。
- Predicate.arguments 必须是列表，不接受具名映射；参数名和类型由 Predicate.parameters 定义。
- Operation / Observation.arguments 必须是映射，不接受位置列表；参数名和类型由 Owner Input / Query Schema 定义。

### 13.3 静态校验

Compiler 必须验证：
- 参数名在目标 Schema 中存在；
- 所有 Required 参数均提供；
- 不得传入未声明字段；
- Source Path 在当前控制流路径上可用；
- Source Schema 可赋给目标字段 Schema；
- Optional、Nullability、enum、const、范围和数组元素约束兼容；
- 来源的 Subject、Session、Lifecycle 和 Evidence Scope 没有被不安全地扩大；
- Reconcile 不接受普通 arguments，而引用原始 Mutation Invocation。

### 13.4 最小输入与无隐式转发

只传递目标契约实际需要的字段。不得自动转发调用方全部字段，不得从父 Procedure、Context 或上一个 Node 猜字段，不得根据字段同名自动绑定。Optional 字段默认省略；省略不等于 null；JSON Schema default 不授权 Compiler 自动生成值。

Skill Studio 可以通过语义身份和 Schema 提供参数补全、批量生成显式映射，但保存后的源码必须完整呈现最终参数映射。

## 14. PredicateSet

~~~yaml
predicates:
  createdsession.udm.subscription_usable:
    parameters:
      - subscription: fivegc-tools::urn:connectionagent:5gc:tool-output:udm-subscription-result:v1
      - requestedDnn: string
    evaluator:
      type: cel
      expression: subscription.dnn == requestedDnn &&
        subscription.status == "ACTIVE"
~~~

规则：
- parameters 是有序列表；
- 每项必须是单键映射；
- 参数名唯一；
- 类型为受支持 Primitive 或精确 Schema 引用；
- 结构化对象必须引用 Owner Schema；
- Precondition / Postcondition 的 arguments 数量必须完全一致，顺序必须一致；
- 不允许隐式 Optional、跳过位置、自动 null、类型猜测或重排；
- Predicate 签名是唯一业务输入契约。

当前 Evaluator 支持 CEL 和 Skill 自有 Script。Predicate 不得调用 Tool、Observation、网络、文件系统、时钟、随机数或全局 Context，也不得修改外部状态。

结果：
- PASS：输入和 Evidence 足以支持命题成立；
- FAIL：输入和 Evidence 足以支持命题不成立；
- UNKNOWN：无法可靠判断。

UNKNOWN 不是 FAIL 的别名，也不是“先通过再说”。Evidence 缺失、冲突、过期、Scope 不匹配或来源不可信时，不得接受没有依据的 PASS。

初始 Primitive：string、integer、number、boolean。结构化对象和数组使用 Schema 引用。Compiler 必须逐个绑定点检查 Source Schema 是否可赋给 Target Schema，并覆盖 integer / number、enum / const、required / optional、nullable / omitted、additionalProperties、数组元素、范围约束和组合 Schema。未支持的 Schema 关键字不得静默忽略；最终兼容矩阵需通过正负例冻结。

---

# 第五部分：Observation 与 Evidence


## 15. Observation Query 调用时机

仅在以下情况执行 Observation Query：
1. Invocation 缺少所需事实；
2. 前序 Operation Result 没有提供该事实；
3. Context Projection 不足以满足 Scope / Freshness / Authority；
4. 必须向事实 Owner 查询当前状态；
5. 业务规则要求独立核实。

不应增加 Observation Query：
- 前序 Operation Result 已提供精确值和充分 Evidence；
- Context Projection 已是 Host 信任的权威输入；
- 只是为了每个 Predicate 都有独立读取结果；
- 只是为了轮询某个 Operation 的内部异步完成；
- 只是为了重复构造 Evidence ref。

## 16. Observation Scope 与时间

Observation Query 必须声明 Scope。5GC 场景可能涉及 Environment、UE / SUPI 可信引用、PSI、PTI、DNN、S-NSSAI、Lifecycle Ref、Policy Association Ref、N4 Session Instance Ref、Operation / Invocation / Transaction Ref。

不是每次查询都需要全部维度，必需项由 Owner Schema 和 Query Contract 声明。但结果 MUST 能证明属于调用方期望的 Scope。不能因为 UE 相同就混用不同 PSI、生命周期或 Session Instance。

至少区分：
- eventTime：事实或事件发生时间；
- observedAt：Owner 读取或确认事实的时间；
- receivedAt：Host 收到结果的时间。

Freshness 由 Owner Contract 声明并由 Runtime 验证。旧事件、错误 Lifecycle、错误 Correlation 或过期结果不能证明当前状态。

## 17. Evidence 与 Predicate 参数

业务参数与 Evidence 分开传递。建议 Script Evaluation Context：

~~~python
input = {
    "udmResult": {
        "subscription": {
            "dnn": "internet",
            "status": "ACTIVE"
        }
    },
    "requestedDnn": "internet",
    "evidence": {
        "udmResult": {
            "refs": ["evidence-ref-1"]
        }
    }
}
~~~

udmResult 和 requestedDnn 是业务参数；input.evidence 是 Host / Runtime 生成的保留命名空间。Skill 不得绑定或覆盖 evidence。Evidence Ref 不是业务 Payload。Predicate 的业务参数名 evidence 应保留并禁止，以免冲突。

一个业务参数可以不需要 Evidence（例如 Skill 常量），可以关联一个 Evidence Ref，也可以关联多个 Evidence Ref（例如聚合值由多个权威来源支持）。是否需要 Evidence、需要多少条、是否必须来自同一 Owner，由 Predicate 语义要求和 Owner / Host 保证共同决定。

Runtime MUST 验证 Evidence 存在、Invocation 可访问、与 Producer / Payload 关联成立、Subject / Session / Lifecycle 一致、时间和 Freshness 满足要求且不存在未解决冲突。缺少必要 Evidence 时结果为 UNKNOWN 或拒绝执行，不得自动 PASS。

Predicate Script 可以声明实际使用的 Evidence Ref，但只能是 Host 已附加集合的子集。Script 不得新建、引入未附加、重绑、扩大 Scope 或自行宣称可信 Evidence。

## 18. Fact、Observation、Evidence、State 的区别

| 名称 | 回答的问题 | 示例 |
|---|---|---|
| Fact | 要判断的业务命题是什么？ | UE 目标 Session 已建立 |
| Operation Result | 一次操作返回了什么？ | PCF Create 返回 association handle |
| Observation Query | 如何向权威 Owner 查询？ | 查询 SMF N4 资源状态 |
| Observation Result | Owner 返回什么事实？ | 当前 Session 对应 N4 pair |
| Evidence | 为什么相信这个值？ | Owner 记录、Invocation、Correlation、时间 |
| State | Host / Owner 保存什么状态？ | 生命周期、资源责任记录 |
| Context Projection | Skill 被允许读取什么？ | 当前 Invocation Subject / Facts / Ingress |

State 不自动等于 Evidence；Handle 不自动等于 State；Mutation 成功不自动等于业务 Fact；Observation Result 不自动等于 PASS；Evidence Ref 不包含业务 Payload。

---

# 第六部分：执行语义、异常与恢复

## 19. Invocation 生命周期

1. Host 接收 Invocation；
2. Host 构造可信 Subject、Request、Ingress 和 Context Projection；
3. Root Router 选择唯一 Skill；
4. Host 校验入口、授权和运行条件；
5. Runtime 创建隔离 Invocation；
6. Procedure 从明确入口执行；
7. 每个 Node 按绑定、Preconditions、主动作、Postconditions 和路由执行；
8. 必要时显式执行 Observation Query；
9. Predicate 消费已物化输入和 Evidence；
10. Mutation 结果不确定时对原 Mutation Reconcile；
11. 执行 Skill 最终 Postconditions；
12. Host 记录结果、Evidence、Trace 和资源责任。

必需步骤不得静默跳过。

## 20. READ、MUTATION 与 Reconcile

READ 仍须验证 Capability、Effect、Input Schema、Scope、Output Schema、Producer Invocation 和 Evidence，并防止越权读取其他 UE / Session。

MUTATION 可能产生外部副作用。执行前 Runtime 必须验证授权、Effect、Input Schema、Invocation / Subject / Lifecycle / Correlation、Precondition、Deadline 和取消状态，并记录精确 Operation 身份。

执行后必须区分已确认提交、明确未提交、明确失败和结果不确定。网络超时不能直接解释为远端没有执行。

请求可能已到达远端但响应丢失时：
- 不得直接发送新的 Mutation；
- 保留原始 Operation Ref / Invocation / Transaction / Correlation；
- Reconcile 原 Mutation；
- 只有明确证明未提交且业务契约允许时，才能发起新的受控尝试；
- Reconcile 仍无法判断时，结果保持 UNKNOWN / UNRESOLVED。

Reconcile 不是普通重试。它必须指向原 Mutation，保留原 Scope / Correlation，不得产生新的业务 Mutation。

## 21. 异步 Operation：没有 Skill Wait

vNext 不定义 Skill 层 wait、await、polling node，也不要求 ca.session.evidence.await 作为 Skill callable。

异步协议交互属于执行该协议动作的 Tool / Provider / SMF Operation。例如：
- UPN.CREATE_UP_SESSION 负责内部 N4 Session 建立和完成确认；
- SSM.SIGNAL_UE_AN 负责内部 RAN signaling / adoption 完成；
- UPN.MODIFY_UP_SESSION 负责内部 N4 forwarding 修改和完成确认。

这些 Operation 在返回最终成功时，必须提供最终规范化结果和关联 Evidence。Procedure 只在最终结果可用后进入下一步。

Host / Runtime 仍负责 Deadline、Cancellation、Correlation、预算、UNKNOWN 和超时后的 Reconcile。这些 Runtime 控制不是 Skill 作者定义的 Wait Loop。

上述三个 Operation 是目标设计映射；真实 ToolCatalog、输入输出和 Evidence 契约仍须由 Owner 确认，不能因为本规范写出名称就声称已经实现。

## 22. 路由结果

Predicate：PASS 表示命题得到充分支持；FAIL 表示命题被充分证伪；UNKNOWN 表示无法可靠判断。

Operation 路由可包含 SUCCEEDED、FAILED、DENIED、NOT_COMMITTED、OUTCOME_UNKNOWN 等由 Runtime 明确声明的状态。每个可达结果必须有显式路由，或按规范作为终止错误。未识别状态不得映射为 SUCCEEDED。

## 23. 并发、UE 与 Session 隔离

Skill Package 是静态定义，不是 UE 全局记忆。每次 Invocation 的状态必须通过 Host / Runtime 隔离上下文访问。

~~~text
Environment
 └── UE / Subject
      └── Lifecycle
           └── PDU Session (PSI)
                ├── PTI / Request
                ├── Policy Association
                └── N4 Session Instance
                     ├── SMF SEID
                     └── UPF SEID
~~~

这是概念层次，不是所有网元内部数据结构的强制定义。

不得只用 SUPI 作为所有资源的唯一选择条件；不得混用 PSI 相同但 Lifecycle 不同的记录；不得把 Pre-N4 Policy Association 当作 Post-N4 Session Instance；不得跨 Invocation 复用 Evidence；不得在并发 UE 之间共享可变 Predicate 输入；不得用全局缓存“最新一条”决定资源归属。

## 24. 错误分类

错误分为源代码错误、静态契约错误、Runtime 执行错误和业务结果。不得把它们压缩成含义不清的 FAILED。

### 24.1 Compiler 静态错误

| 错误 | 示例 | 要求 |
|---|---|---|
| YAML_PARSE_ERROR | 缩进、重复 Key、非法类型 | 阻止构建 |
| ROOT_KIND_INVALID | 根 kind 错误 | 阻止构建 |
| API_VERSION_UNSUPPORTED | 不支持版本 | 阻止构建 |
| UNKNOWN_FIELD | 未定义语义字段 | 阻止构建 |
| DUPLICATE_ID | Procedure / Node / Predicate 重名 | 阻止构建 |
| ENTRY_PROCEDURE_MISSING | 入口不存在 | 阻止构建 |
| CONTROL_FLOW_DANGLING | 路由指向不存在 Node | 阻止构建 |
| CONTROL_FLOW_AMBIGUOUS | 多个主动作 | 阻止构建 |
| DEPENDENCY_ALIAS_MISSING | Alias 不存在 | 阻止构建 |
| EXPORT_ID_MISSING | callable / Schema 不存在 | 阻止构建 |
| EXPORT_ID_AMBIGUOUS | 导出身份歧义 | 阻止构建 |
| SCHEMA_MISSING / INVALID | 缺失或非法 Schema | 阻止构建 |
| INPUT_REQUIRED_MISSING | 缺少必填输入 | 阻止构建 |
| INPUT_TYPE_MISMATCH | Source 不可赋给 Target | 阻止构建 |
| INPUT_NULLABILITY_MISMATCH | nullable Source 绑定非 nullable Target | 阻止构建 |
| SOURCE_NOT_AVAILABLE | Producer 非所有路径可用 | 阻止构建 |
| PREDICATE_ARITY_MISMATCH | 参数数量不一致 | 阻止构建 |
| PREDICATE_TYPE_MISMATCH | 参数类型不兼容 | 阻止构建 |
| CAPABILITY_NOT_GRANTED | 未授予 Capability | 阻止构建 |
| CAPABILITY_MAPPING_MISSING | callable 没有唯一 Capability | 阻止构建 |
| EFFECT_MISMATCH | Tool 与 Capability Effect 不一致 | 阻止构建 |
| SCRIPT_CONTRACT_INVALID | Script 入口 / TypedDict 不合规 | 阻止构建 |
| UNSUPPORTED_WAIT | 出现 Wait / Await | 阻止构建 |
| UNSUPPORTED_V02_SYNTAX | 使用旧版隐式语法 | 阻止构建 |

Compiler 不得为让文件编译而创建不存在的 Schema、用 object 逃逸、猜测 Operation ID、扩大 Capability、把 UNKNOWN 改成 PASS、静默删除未知字段或把旧语法映射成新语义。

### 24.2 Runtime 异常

| 异常 | 处理原则 |
|---|---|
| AUTHORIZATION_DENIED | 不调用 Tool，返回 DENIED |
| EFFECT_MISMATCH | Fail-closed |
| TOOL_UNAVAILABLE | 按契约区分 FAILED / UNKNOWN |
| INPUT_VALIDATION_FAILED | 拒绝调用 |
| OUTPUT_SCHEMA_INVALID | 不得消费为可信结果 |
| SCOPE_MISMATCH | 拒绝结果，Predicate UNKNOWN |
| CORRELATION_MISMATCH | 拒绝结果 |
| EVIDENCE_MISSING | UNKNOWN 或拒绝 |
| EVIDENCE_STALE | UNKNOWN |
| EVIDENCE_CONFLICT | UNKNOWN / unresolved |
| DEADLINE_EXCEEDED | 取消后续动作，确认已发起副作用状态 |
| CANCELLED | 不启动新动作；必要时 Reconcile |
| OUTCOME_UNKNOWN | Reconcile 原 Mutation |
| RECONCILE_UNRESOLVED | UNRESOLVED，不盲目重试 |
| DUPLICATE_RESOURCE | 按业务规则 FAIL / Reconcile |
| STALE_LIFECYCLE | 停止当前尝试 |
| PARTIAL_COMPLETION | 明确资源责任和恢复策略 |
| OWNER_CONTRACT_UNAVAILABLE | UNKNOWN / unresolved |
| CONCURRENT_MODIFICATION | 重新验证 Scope 和版本，不覆盖未知状态 |

## 25. 典型业务异常

- **UE 尚未注册：** 必须通过可信 Host Context 或 Owner Observation 证明。请求中有 SUPI 不代表 UE 已注册。明确未注册按业务规则 FAIL；无法查询则 UNKNOWN。
- **UDM 无数据：** 明确无订阅数据可按业务规则 FAIL；UDM 不可用则 UNKNOWN；UE / DNN / S-NSSAI 不匹配则拒绝结果；不得用上一个 UE 缓存补齐。
- **UDM Subscribe 响应丢失：** 不得重新发送新 Subscribe。必须 Reconcile 原始 Mutation。确认已提交则复用原结果；确认未提交且业务契约允许才可新尝试；无法判断则 UNRESOLVED。
- **PCF Association 已存在：** Create 前验证准确的 Pre-N4 状态。已有冲突 Association 必须停止 Create。查询为空与查询失败不能混为一谈。
- **N4 尚未完成：** N4 异步建立属于 UPN.CREATE_UP_SESSION 内部完成责任。不得在最终完成前返回成功。结果必须关联本次 Policy Association、Lifecycle 和 Session Instance。Skill 不定义 Wait Loop。
- **AMF N1/N2 Transfer 部分失败：** 区分请求未发送、已发送但未知、明确失败和明确成功。传输超时不能解释为 AMF 未收到。保留 Operation Ref、目标 AMF、Response Artifact 和 Evidence。
- **RAN Setup 成功但 N4 Forwarding 失败：** 不得将 Session 标记成功。记录已完成资源和未完成资源，明确资源责任 Owner，进入 FAILED 或 UNRESOLVED。
- **多 Invocation 并发同一 UE：** 使用各自 Invocation / Lifecycle / PSI / Operation Ref。不能通过“最新记录”选择资源，不能把 A 的 Hold 用到 B 的 Mutation。
- **同一 UE 的两个 PSI：** PSI 必须参与 Session Scope。一个 PSI 的 N4 / Policy Association 不得绑定到另一个 PSI。
- **Observation 过期或冲突：** 过期结果不能证明当前状态；不同 Lifecycle 结果不能合并；多个 Owner 冲突时不能任意选择。无法消除冲突则 UNKNOWN。

---

# 第七部分：PDU Session 简化示例

## 26. 示例说明

本节展示语言结构，不重建全部 5GC ToolCatalog 或 36 个 Case。字段是教学示意，不构成 Owner Schema 发布声明。

流程：UE 注册验证 → UDM 查询 → UDM Subscription → PCF Association → N4 建立 → N1/N2 Transfer → RAN Setup → N4 Forwarding → 最终验证。

真实 Owner Input / Output Schema、Effect、Capability 和 Evidence 必须由 Owner 发布。

## 27. Request Schema

~~~yaml
$schema: https://json-schema.org/draft/2020-12/schema
$id: establishment-request.schema.yaml
type: object
additionalProperties: false
required: [pduSessionId, pti, requestType, dnn, sNssai]
properties:
  pduSessionId:
    type: integer
    minimum: 1
    maximum: 15
  pti:
    type: integer
    minimum: 1
    maximum: 254
  requestType:
    type: integer
  dnn:
    type: string
    minLength: 1
  sNssai:
    type: object
    additionalProperties: false
    required: [sst]
    properties:
      sst:
        type: integer
        minimum: 0
        maximum: 255
      sd:
        type: [string, "null"]
~~~

UE 身份来自 Host Subject，而不是调用方任意伪造的 UE Ref。

## 28. SkillContract

~~~yaml
apiVersion: connectionagent.io/v1alpha2
kind: SkillContract
metadata:
  name: establish-pdu-session
spec:
  skillType: executable
  goal: pdu_session.initial_request_fulfilled
  entryProcedure: establish
  inputs:
    requestSchema: schemas/establishment-request.schema.yaml
  context:
    projections:
      subject: host-context::urn:connectionagent:5gc:skill-context:subject:v1
      ingress: host-context::urn:connectionagent:5gc:skill-context:ingress:v1
      facts: host-context::urn:connectionagent:5gc:skill-context:facts:v1
    evidenceSchema: host-context::urn:connectionagent:host:predicate-evidence-refs:v1
  allowedResources:
    capabilities:
      - fivegc-session-read
      - fivegc-session-mutation
      - fivegc-session-assurance
  postconditions:
    - predicate: createdsession.session.established
      expect: PASS
~~~

Skill 不直接 grant Operation，只授予部署侧定义的 Capability。

## 29. PredicateSet

~~~yaml
predicates:
  createdsession.ue.registered:
    parameters:
      - registration: fivegc-observations::urn:connectionagent:5gc:observation:ue-registration:v1
    evaluator:
      type: cel
      expression: registration.state == "REGISTERED" &&
        registration.accessState == "ACTIVE"

  createdsession.udm.subscription_usable:
    parameters:
      - subscription: fivegc-tools::urn:connectionagent:5gc:tool-output:udm-subscription-result:v1
      - requestedDnn: string
    evaluator:
      type: cel
      expression: subscription.dnn == requestedDnn &&
        subscription.status == "ACTIVE"

  createdsession.session.established:
    parameters:
      - ranSetup: fivegc-observations::urn:connectionagent:5gc:observation:ran-setup-result:v1
      - n4Forwarding: fivegc-observations::urn:connectionagent:5gc:observation:n4-forwarding-result:v1
    evaluator:
      type: cel
      expression: ranSetup.accepted == true &&
        n4Forwarding.forwardingReady == true &&
        ranSetup.sessionInstanceRef == n4Forwarding.sessionInstanceRef
~~~

## 30. Procedure

~~~yaml
procedures:
  establish:
    inputs:
      ueRef: context.subject.ueRef
      pduSessionId: context.request.pduSessionId
      pti: context.request.pti
      dnn: context.request.dnn
      sNssai: context.request.sNssai
    start: observe-ue-registration
    nodes:
      observe-ue-registration:
        observation: fivegc-observations::ue.registration.current
        arguments:
          ueRef: input.ueRef
        'on':
          SUCCEEDED: check-ue-registration
          FAILED: failed
          UNKNOWN: unresolved

      check-ue-registration:
        precondition:
          predicate: createdsession.ue.registered
          arguments:
            - observe-ue-registration.output
        'on':
          PASS: read-udm-subscription
          FAIL: failed
          UNKNOWN: unresolved

      read-udm-subscription:
        operation: fivegc-tools::sbi.udm.sm_data.get
        arguments:
          ueRef: input.ueRef
          dnn: input.dnn
          sNssai: input.sNssai
        'on':
          SUCCEEDED: check-udm-subscription
          FAILED: failed
          DENIED: failed
          UNKNOWN: unresolved

      check-udm-subscription:
        postcondition:
          predicate: createdsession.udm.subscription_usable
          arguments:
            - read-udm-subscription.output.result
            - input.dnn
        'on':
          PASS: create-udm-subscription
          FAIL: failed
          UNKNOWN: unresolved

      create-udm-subscription:
        operation: fivegc-tools::sbi.udm.sdm_subscription.create
        arguments:
          ueRef: input.ueRef
          subscription: read-udm-subscription.output.result
        'on':
          SUCCEEDED: create-pcf-association
          NOT_COMMITTED: failed
          OUTCOME_UNKNOWN: reconcile-udm-subscription
          DENIED: failed
          FAILED: failed

      reconcile-udm-subscription:
        operation:
          reconcile: create-udm-subscription
        'on':
          COMMITTED: create-pcf-association
          NOT_COMMITTED: failed
          UNRESOLVED: unresolved

      create-pcf-association:
        operation: fivegc-tools::sbi.pcf.sm_policy.create
        arguments:
          ueRef: input.ueRef
          pduSessionId: input.pduSessionId
          dnn: input.dnn
          sNssai: input.sNssai
        'on':
          SUCCEEDED: verify-pcf-association
          NOT_COMMITTED: failed
          OUTCOME_UNKNOWN: reconcile-pcf-association
          DENIED: failed
          FAILED: failed

      verify-pcf-association:
        postcondition:
          predicate: createdsession.pcf.association_owned
          arguments:
            - create-pcf-association.output
        'on':
          PASS: create-n4-session
          FAIL: failed
          UNKNOWN: unresolved

      reconcile-pcf-association:
        operation:
          reconcile: create-pcf-association
        'on':
          COMMITTED: verify-pcf-association
          NOT_COMMITTED: failed
          UNRESOLVED: unresolved

      create-n4-session:
        operation: fivegc-tools::UPN.CREATE_UP_SESSION
        arguments:
          ueRef: input.ueRef
          pduSessionId: input.pduSessionId
        'on':
          SUCCEEDED: transfer-n1n2
          OUTCOME_UNKNOWN: unresolved
          FAILED: failed
          DENIED: failed

      transfer-n1n2:
        operation: fivegc-tools::sbi.amf.n1n2.transfer
        arguments:
          ueRef: input.ueRef
          pduSessionId: input.pduSessionId
        'on':
          SUCCEEDED: signal-ran
          OUTCOME_UNKNOWN: unresolved
          FAILED: failed
          DENIED: failed

      signal-ran:
        operation: fivegc-tools::SSM.SIGNAL_UE_AN
        arguments:
          ueRef: input.ueRef
          pduSessionId: input.pduSessionId
        'on':
          SUCCEEDED: modify-n4-forwarding
          OUTCOME_UNKNOWN: unresolved
          FAILED: failed
          DENIED: failed

      modify-n4-forwarding:
        operation: fivegc-tools::UPN.MODIFY_UP_SESSION
        arguments:
          ueRef: input.ueRef
          pduSessionId: input.pduSessionId
        'on':
          SUCCEEDED: inspect-final-state
          OUTCOME_UNKNOWN: unresolved
          FAILED: failed
          DENIED: failed

      # 本示例假设 Operation Result 尚不足以独立证明最终 N4 / RAN 资源一致性，
      # 因此显式查询权威状态。若 Operation Result 已满足 Predicate 的全部要求，
      # 可直接从 modify-n4-forwarding 路由到 verify-final-state。
      inspect-final-state:
        observation: fivegc-observations::session.establishment.final_state
        arguments:
          ueRef: input.ueRef
          pduSessionId: input.pduSessionId
          sessionInstanceRef: create-n4-session.output.sessionInstanceRef
        'on':
          SUCCEEDED: verify-final-state
          FAILED: failed
          UNKNOWN: unresolved

      verify-final-state:
        postcondition:
          predicate: createdsession.session.established
          arguments:
            - signal-ran.output.result
            - modify-n4-forwarding.output.result
            - inspect-final-state.output
        'on':
          PASS: complete
          FAIL: failed
          UNKNOWN: unresolved

      complete:
        terminal: SUCCEEDED
      failed:
        terminal: FAILED
      unresolved:
        terminal: UNRESOLVED
~~~

说明：
- 四种业务节点分别是 Precondition、Operation、Observation、Postcondition。Terminal 只是终止声明；Predicate 是被引用的确定性逻辑，不是节点。
- Observation 不是 Operation 的必经步骤。本示例只在假设 Operation Result 不足以证明最终状态时才查询；若 Operation 已提供充分结果和 Evidence，可直接执行 Postcondition。
- Observation 可以使用 Operation Result 中的 Session Instance Ref 作为查询参数，但查询结果必须由 Observation Owner 实际产生，不能伪装来源。
- UPN.CREATE_UP_SESSION、SSM.SIGNAL_UE_AN、UPN.MODIFY_UP_SESSION 是目标设计中的异步完成责任映射，不代表 Owner 已发布正式 ToolCatalog。
- 示例中的 dependency alias、Schema ID 和字段是教学示意，不是当前依赖快照的可链接声明。
- 示例未展开 PCF Hold、UDM Hold、Lifecycle Gate、资源责任和完整 Reconcile，不得代替真实 5GC Skill。
- 真实主线必须保留既有业务顺序和 Owner 约束，不能因示例简化而移除 Hold / Lifecycle / Correlation。

## 31. Operation 与 Observation 对照

~~~yaml
# Operation：执行一个业务动作
create-policy:
  operation: fivegc-tools::sbi.pcf.sm_policy.create
  arguments:
    ueRef: input.ueRef
    pduSessionId: input.pduSessionId

# Observation：只有在需要补充权威事实时才查询
read-policy-state:
  observation: fivegc-observations::pcf.policy_association.current
  arguments:
    ueRef: input.ueRef
    pduSessionId: input.pduSessionId

# Postcondition：如果 Operation Result 已经充分，也可以不创建 Observation 节点
verify-policy:
  postcondition:
    predicate: createdsession.pcf.association_owned
    arguments:
      - create-policy.output
~~~

Operation 与 Observation 共用 ToolCatalog、Capability 和 Runtime Admission，但业务语义不同。Observation 是可选的事实获取机制，不是 Operation 的固定后继。Operation Result 可以直接作为 Predicate 输入；若需要独立权威查询，则 Observation 可以使用 Operation Result 中的资源引用和关联身份作为 arguments。

## 32. Python Script

Python Script 是 Predicate 的一种确定性 evaluator 实现，不是独立 Procedure Node，也不是 Tool。简单逻辑优先使用 CEL；只有当判断逻辑确实需要 Python 表达能力时，才使用 Script。

唯一入口：

~~~python
from typing import Literal

PredicateOutcome = Literal["PASS", "FAIL", "UNKNOWN"]

def main(input: dict) -> PredicateOutcome:
    subscription = input["subscription"]
    requested_dnn = input["requestedDnn"]

    if subscription["dnn"] != requested_dnn:
        return "FAIL"
    if subscription["status"] != "ACTIVE":
        return "FAIL"
    return "PASS"
~~~

规则：
- 入口必须为 `main(input: dict) -> PredicateOutcome`；
- input: dict 是统一调用容器，不代表开放输入契约；
- 业务输入类型由所属 Predicate.parameters 派生；
- Host / Runtime 可以附加只读 Evidence refs；Script 不得创建、修改或扩大 Evidence；
- 返回值只能是 PASS、FAIL、UNKNOWN，其他值均为契约错误；
- Compiler / LSP 必须提供由 Predicate.parameters 派生的只读类型环境；
- 不得动态推断参数 Schema 或执行 Python 函数体来猜测类型；
- 不得访问网络、HTTP、MCP、Shell、数据库、文件系统、凭据、环境变量、时钟或随机源；
- 不得声明 Tool ID、Operation ID、Capability ID 或独立 Input Schema。

Python Script 只承载 Predicate 的确定性判断。数据获取必须由显式 Operation / Observation 完成；流程分支必须由 Procedure 的 Predicate 结果路由完成。

## 33. Cases

Case 是场景声明，不是执行图。可以记录场景输入、预期业务语义、路由、资源不变量、失败 / UNKNOWN 条件。Case 不得自行授予 Capability、定义 Tool Schema、代替 Owner Evidence 或声称已执行通过。

## 34. Dependencies 与 BuildRequest

Skill 源码引用 Skill 自有文件的包内路径，或 Dependency Alias + Owner 精确导出身份。不得包含 Git URL、branch、仓库路径、下载地址、digest、lockfile、registry 地址或依赖获取指令。

Compiler 概念输入：

~~~typescript
type File = { path: string; bytes: Uint8Array };
type DependencySnapshot = { alias: string; files: File[] };
type BuildRequest = {
  files: File[];
  dependencies: DependencySnapshot[];
  capabilityContracts: File;
  targets?: string[];
};
~~~

Compiler MUST 只消费调用方提供的字节；验证路径、重复文件、重复 Alias、重复导出身份、Schema、引用、Binding、Capability 和 Effect；返回诊断和生成文件。

Compiler MUST NOT 联网获取依赖、管理版本 / Lock / Cache / Workspace、执行 Python、执行 Tool 或声称 Runtime READY。

## 35. Skill Studio 与 LSP

Skill Studio 是 CA-SL 作者工作环境，不是第二个语言实现。应提供：

1. YAML 语法、缩进、字段补全和非法字段提示；
2. Skill / Procedure / Node / Operation / Observation / Capability / Predicate / Schema / Script 语义高亮；
3. Definition：跳转 ToolCatalog、Owner Schema 和 Python Script；
4. References：查询调用点；
5. Hover：Owner、Effect、Schema、Capability、Scope / Freshness / Evidence 保证；
6. Completion：只补全当前依赖快照中真实存在的导出身份；
7. Diagnostics：区分语法、链接、类型、授权和业务警告；
8. Procedure Designer：显示真实执行图、Node、Step、Predicate 和分支；
9. Data Flow：展示 Context / Operation / Observation 到 Predicate 的值流和 Evidence 关联；
10. Package View：区分 Skill 自有文件、只读依赖和生成 Artifact；
11. Case View：展示语义义务，不伪装成 Runtime 结果；
12. Owner Inspection：展示 Schema / Tool / Observation 的 Owner 和导出身份。

语法颜色不代表链接成功；Definition 能跳转不代表 Runtime 已授权；Schema Completion 不代表 Tool 已部署；Build PASS 不代表真实 5GC PASS；Case 已定义不代表已执行；Evidence Ref 可见不代表校验通过。

---

# 第九部分：参考语言与设计取舍

## 36. CUE

参考：https://cuelang.org/docs/reference/spec/

借鉴正式语言规范、类型约束、Schema 组合和 IDE 可分析性。CA-SL 不直接采用 CUE 作为主语言，因为还需要 Procedure 控制流、Capability 授权、Operation / Observation 边界和 Evidence 语义。Schema 可使用 JSON Schema，Predicate 可使用 CEL。

## 37. Temporal

参考：
- https://docs.temporal.io/workflow-definition
- https://docs.temporal.io/workflows
- https://docs.temporal.io/encyclopedia/retry-policies

借鉴 Workflow Definition 与 Execution 区分、确定性编排、外部副作用隔离、重试和恢复语义。

CA-SL 不自带 Temporal 式持久化 Workflow Engine，也不使用通用语言编写 Workflow。CA-SL 的核心扩展是 Owner、Capability、Observation、Evidence 和受约束的 Skill Procedure。

## 38. OpenAPI

参考：https://spec.openapis.org/oas/latest.html

借鉴 Operation 身份、参数、Request / Response Schema 和引用机制。CA-SL 不取代 OpenAPI；Tool Owner 可以用 OpenAPI 描述 HTTP API，但 ToolCatalog 还需表达 Effect、Capability、Adapter、Evidence 和 Reconcile 契约。

## 39. AsyncAPI

参考：
- https://www.asyncapi.com/docs/concepts/asyncapi-document/structure
- https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-operations

借鉴消息、Channel、Operation、Correlation ID 和异步交互的明确建模。CA-SL 不把异步网元交互简化为 Skill Wait Loop；异步完成归属对应 Tool / Provider Operation。

## 40. RFC 2119 / RFC 8174

参考：
- https://www.rfc-editor.org/rfc/rfc2119
- https://www.rfc-editor.org/rfc/rfc8174

用于统一规范性措辞。

## 41. CA-SL 的定位

| 关注点 | 参考 | CA-SL 扩展 |
|---|---|---|
| Schema / 类型 | CUE、JSON Schema | Owner、依赖和静态 Binding |
| API Operation | OpenAPI | Effect、Capability、Runtime Admission |
| 异步消息 | AsyncAPI | Operation / Observation / Evidence / Reconcile |
| 确定性工作流 | Temporal | 声明式 Procedure 和副作用边界 |
| 规范写法 | RFC | 术语、语法、语义和符合性 |

CA-SL 的定位是**受治理的确定性业务编排语言**，不是普通 Workflow YAML 或 Tool Calling Prompt。

---

# 第十部分：安全、版本与冻结

## 42. 信任模型

信任边界包括 Skill 源码、DependencySnapshot、ToolCatalog、Owner Schema、CapabilityContracts、Host Context、Operation Result、Observation Result、Evidence 和 Script。每类数据必须保留来源和 Owner 身份。

## 43. 安全要求

Skill 不得声明任意 HTTP Endpoint 或凭据；Script 不得自行调用网络、Shell、数据库或文件系统；Compiler 不得通过网络解析 Schema；外部引用必须来自本次 BuildRequest；路径穿越、重复身份和歧义引用必须 fail-closed；Tool / Observation 调用必须经过 Capability 和 Effect 检查；Runtime 必须按 Invocation / Subject / Lifecycle 隔离；Evidence 必须由可信 Producer / Host 关联；Observation Query 必须进行 Scope 检查；模型输出、Script 输出和本地变量不得扩大授权。

## 44. 版本策略

必须区分语言版本、API Version、ToolCatalog Version、Schema $id / Version、CapabilityContracts Version 和 Skill Package Revision。它们不能互相冒充。

vNext 是破坏性收敛，不要求保留 v0.2 隐式输入、旧 ObservationSource Predicate 声明、直接 Operation Grant、Skill Wait 或 package-local lib 导入路径。

迁移必须证明业务顺序、Scope、Correlation、Freshness、Evidence 和失败语义没有被削弱。

## 45. 冻结门槛

1. 术语与概念模型评审；
2. ToolCatalog Operation / Observation typed callable 结构定稿；
3. CapabilityContracts callable membership 定稿；
4. Observation Query 调用和 QueryContext 绑定语法定稿；
5. Evidence 与 Predicate 参数关联模型定稿；
6. Schema ID 和 Dependency Alias 引用规则定稿；
7. Predicate 类型系统、CEL 和 Python 类型环境定稿；
8. Procedure Node、Step、Pre/Postcondition 和路由正负例；
9. 三个 5GC 异步完成 Operation 的 Owner 契约确认；
10. 完整 5GC PDU Skill 迁移演练；
11. Compiler 正负例与诊断验收；
12. Skill Studio 语义体验验收；
13. Native / WASM / Studio 语义一致性验证。

在以上事项完成之前，状态保持 DESIGN REVIEW。不得把候选 YAML 结构描述为已发布 Owner 契约。

---

# 第十一部分：评审 FAQ

## 46. 为什么不直接使用 OpenAPI？

OpenAPI 描述 API 接口、参数和响应，但不完整描述 Skill 业务目标、确定性流程、Predicate、Evidence、Capability 授权、Reconcile 和多步骤恢复。CA-SL 可以引用 Tool Owner 发布的契约，两者不是竞争关系。

## 47. 为什么不直接用 Temporal？

Temporal 是持久化 Workflow 执行平台，CA-SL 不重新实现它。CA-SL 是面向 Agent Skill 的受约束声明语言，重点在 Tool Owner、Capability、Observation、Evidence 和 Studio 语义编辑。未来可以研究映射到底层执行平台，但不是语言规范前提。

## 48. Observation 为什么不能只是 Predicate 的数据字段？

Agent 有时必须主动向权威 Owner 查询当前事实。该查询具有输入、权限、Effect、Owner、输出 Schema、Scope 和 Evidence 保证，应是显式可治理的 Tool 调用，而不是 Predicate 内部隐藏获取。同时 Observation 不应拥有独立于 ToolCatalog 的依赖、Schema、Capability 和 Runtime 管理系统。

## 49. Observation 为什么不与 Mutation Operation 一一配对？

Operation 输出有时已经足够；有时一个 Observation 服务多个 Operation；有时一个 Tool 暴露多个查询；有些 Mutation 不需要独立查询。强制一一配对会制造重复查询和无意义接口。

## 50. Operation Result 为什么不能直接叫 Observation？

Operation Result 记录一次操作返回了什么；Observation Result 是 Owner 对事实进行查询后的状态视图。只有 Operation 契约明确保证所需事实、Scope、Correlation、Freshness 和 Evidence 时，才能直接复用。

## 51. 为什么不让 Predicate 自己调用 Observation？

这样 Predicate 就不再是纯函数，会隐藏网络访问、授权、超时、重试、Freshness 和 Evidence 获取。必须先显式查询，再把结果交给 Predicate。

## 52. 为什么不保留 Skill Wait？

Skill 不应了解 SMF Operation 内部如何完成异步协议流程。若 Operation 的业务语义是“建立 N4 Session 并确认最终完成”，它就必须在返回最终成功前完成该责任。Runtime 仍管理 Deadline、Cancellation 和 UNKNOWN，但不把它们变成 Skill 作者的轮询逻辑。

## 53. 为什么 Mutation 超时不能直接重试？

请求可能已经在远端提交，只是响应丢失。直接发第二次可能重复创建资源或副作用。必须先对原 Operation Reconcile。

## 54. 为什么区分 Capability 和 Operation？

Operation 是“能调用什么”；Capability 是“部署允许这一组什么能力”。Skill 可以声明需要某个 Capability，但不能自行把 Operation 加入其中或改变 Effect。

## 55. 为什么 Skill 不直接引用 Tool Adapter？

Adapter 是 Tool Owner 的实现细节。Skill 应引用稳定契约身份，而不是 HTTP URL、Python 类名或网元内部路径。

## 56. 为什么 Schema 不全部放在 Skill 的 schemas/？

因为这会产生影子契约。UDM、SMF、PCF、Host、Fabric 各自拥有不同业务数据和状态。Skill 复制 Schema 会导致 Owner 更新而 Skill 未同步，产生两套矛盾事实。

## 57. 为什么 Script 入口是 input: dict？

dict 只是统一 Python 调用容器，不代表开放输入契约。Script 只实现 Predicate；其业务输入由 Predicate.parameters 派生，Host 可附加只读 Evidence refs。Compiler / LSP 应提供派生类型环境，不让作者维护重复 Schema。

## 58. 为什么不自动把前一个 Node 输出传给下一个？

隐式前序绑定会让节点移动改变语义，使分支路径难以静态验证，也会让同名字段的来源、Scope 和生命周期不明确。Operation / Observation 使用 arguments 具名映射，Precondition / Postcondition 使用有序 arguments 列表；每个消费者必须明确声明数据来源。

## 59. 为什么第一版不保留自动同名绑定？

显式绑定更容易审查，不会因字段重名意外传值。Studio 可以辅助生成显式 Binding。未来若语义 ID、Schema、Scope 和 CFG 可用性能够完整证明，可另行提案。

## 60. 为什么 Evidence 不放进业务 Payload？

业务数据和可信来源是不同东西。把 Evidence 混入业务对象会让 Script、Schema 和业务逻辑承担 Host 信任责任，也容易让业务代码伪造或覆盖 Evidence。Evidence 应由 Host / Runtime 独立附加和校验。

## 61. 为什么需要 UNKNOWN？

现实系统存在信息不足、网络中断、查询失败、Evidence 过期和状态冲突。如果只能 PASS / FAIL，系统会被迫猜测。UNKNOWN 是正确性边界，不是多余复杂度。

## 62. 为什么 MAS 暂时不作为第一验收基线？

传统 5GC PDU Session Skill 有真实执行路径和可核对 Owner 行为，可以验证语言是否忠实表达现有业务。MAS 仍有未完成 Owner ToolCatalog 和 Snapshot 契约，不能用设计稿假装具备可执行能力。

## 63. 为什么 Compiler 不负责依赖获取和包管理？

Compiler 对本次给定字节进行解析、链接和校验。依赖选择、下载、版本锁定、缓存、刷新和工作区持久化属于 Studio / 调用方。否则 Compiler 会膨胀成 Package Manager。

## 64. 为什么 Build PASS 不代表 Skill 可运行？

Build PASS 只说明本次源码和契约满足静态规则。运行还需要 Adapter 注册、Capability 授权、Runtime Admission、外部服务可用、Evidence 真实有效、业务前置条件满足和网元交互成功。

## 65. 为什么需要 Owner 评审？

规范可以定义“必须有什么契约”，但不能代替 Owner 证明实际系统真的提供这些契约。N4、RAN、PCF 的状态字段、Correlation 和 Freshness 必须由 SMF / Provider / Fabric / Host 的真实实现负责，Skill 作者不能编造。

---

## 66. 为什么 Procedure 不再使用通用 call？

通用 call 把业务动作、事实查询和条件判断隐藏在同一种语法下面。CA-SL 用 Precondition、Operation、Observation、Postcondition 表达节点的业务语义，使 Compiler、LSP、Skill Studio 和 Runtime 可以在语法层区分授权、Effect、结果和路由。Terminal 仅声明终态，不是第五种业务动作。

## 67. 为什么 Predicate 不是独立的 computation Node？

Predicate 是确定性计算 / 判断逻辑的定义，使用 CEL 或受约束的 Python Script 实现。Procedure 在需要判断的位置通过 Precondition 或 Postcondition 调用 Predicate。若再增加 computation Node，就会把“判断逻辑定义”和“流程节点位置”重复建模。

## 68. 为什么 Operation 和 Observation 使用具名 arguments，而 Predicate 使用位置 arguments？

Operation / Observation 的输入由 Owner 发布的 JSON Schema 定义，字段名是接口契约的一部分，因此使用具名映射。Predicate 声明有序参数签名，调用时按签名位置传入，因此使用列表。两者都省略 from/value 包装，但静态类型和来源检查不变。

## 69. Operation Result 足够时为什么不执行 Observation？

Observation 是可选的事实获取机制。若 Operation Result 已包含目标 Predicate 所需的业务事实、Scope、Correlation、Freshness 和 Evidence，额外查询只会增加延迟和失败面。只有信息不足或业务明确要求独立权威观察时，才执行 Observation。

## 70. Operation Result 能否作为 Observation 的输入？

可以。Operation Result 可以提供 Observation Query 所需的资源引用、Session Instance、SEID 或 Correlation。但 Observation Result 必须由 Observation Owner 实际查询产生，不能把 Operation Result 包装成 Observation Result，也不能丢失其原始 Producer 身份。

## 71. 为什么 Reconcile 不是独立节点类型？

Reconcile 是原始 Mutation Operation 的受约束调和模式。把它表达为 operation.reconcile: <original-node>，可以复用 Operation 的授权、Owner 契约和 Runtime Admission，同时明确只能调和原始 Mutation，不能发起新的业务 Mutation。

# 附录 A：关键设计决定

| ID | 决定 | 说明 |
|---|---|---|
| D-01 | ca-skills 是 Skill 源码与语言语义唯一权威 | ca-agent-demo 是行为参考 |
| D-02 | vNext 采用破坏性迁移 | 不保留 v0.2 隐式兼容 |
| D-03 | Skill 只 Grant Capability | 不直接 Grant Operation |
| D-04 | Procedure 调用精确 callable | Operation 和 Observation Query 都由 ToolCatalog 解析 |
| D-05 | Observation 是 Tool 体系中的只读查询能力 | 不保留平行 ObservationSource Registry |
| D-06 | Operation Result 与 Observation Result 不混淆 | 复用充分 Operation Result |
| D-07 | Predicate 是纯函数 | 不获取数据、不调用 Tool |
| D-08 | Evidence 与业务 Payload 分离 | Host / Runtime 关联与校验 |
| D-09 | 使用 arguments 显式声明数据来源 | Operation / Observation 具名映射，Predicate 位置参数；不做隐式前序传递 |
| D-10 | 第一版不支持同名自动绑定 | Studio 可以生成显式 arguments 映射 |
| D-11 | Skill 层没有 Wait / Await / Polling | 异步完成归属 Tool / Provider Operation |
| D-12 | Mutation UNKNOWN 必须 Reconcile | 不盲目重试 |
| D-13 | Script 仅实现 Predicate 的确定性逻辑 | 不作为独立 Procedure 节点，不调用外部系统 |
| D-14 | Schema 归真正 Owner 所有 | Skill 不复制外部 Schema |
| D-15 | Compiler 不管理依赖 | Studio / 调用方提供快照 |
| D-16 | Build / Runtime / Network Acceptance 分层 | 不混淆成功含义 |
| D-17 | 多 UE / 多 Session 使用精确 Scope | 不用全局最新状态猜测 |
| D-18 | MAS 不作为第一可执行验收基线 | 先以真实 5GC Skill 验证 |
| D-19 | Procedure 使用四种业务节点 | Precondition / Operation / Observation / Postcondition；Terminal 是终态声明 |
| D-20 | Predicate 是确定性计算 / 判断定义 | 由 Precondition / Postcondition 调用；CEL 或 Python 实现，不设 computation Node |
| D-21 | Observation 遵循结果充分性原则 | Operation Result 足够时直接验证，不强制 Observation |
| D-22 | 调用参数统一使用 arguments | Operation / Observation 具名映射；Predicate 有序位置参数；删除 with/from/value 包装 |
| D-23 | Reconcile 是 Operation 的受约束模式 | 不设独立 Reconcile Node |

# 附录 B：当前状态与待评审事项

本文是可供外部评审的完整设计稿，但仍为 PUBLIC DESIGN REVIEW / NOT FROZEN。

| 项目 | 状态 | 评审责任 |
|---|---|---|
| 术语、概念与职责边界 | 已形成提案 | 架构 / 业务 Owner |
| Procedure 主节点和显式绑定 | 已形成提案 | 语言 / Compiler |
| ToolCatalog typed callable | 候选 YAML，未冻结 | Tool Owner / Compiler |
| CapabilityContracts callable mapping | 候选 YAML，未冻结 | Host / Deployment |
| Observation Query 语法 | 候选表达，待冻结 | Tool Owner / Compiler |
| Evidence 参数关联和 Cardinality | 原则已定义，具体契约待补齐 | Host / Evidence Owner |
| Predicate CEL / Python 类型派生 | 原则已定义，工具链待验证 | Compiler / Studio |
| JSON Schema 支持子集 | 待冻结 | Compiler |
| Applicability / Root Routing | 需与独立契约统一 | Host / Skill |
| 三个异步 Operation Owner 契约 | 目标责任已分配，需确认 | SMF / Provider |
| 5GC 全量迁移 | 未完成 | Skill Owner / Runtime |
| Studio 完整语义体验 | 未完成 | Studio |

评审意见必须归入：规范语义错误、语法表达不清、Owner 契约缺失、Compiler 无法静态验证、Studio 无法正确呈现、Runtime 尚未实现、业务流程尚未验证。不得把所有问题归结为“Compiler 再支持一下”，也不得让 Skill 源码承担其他 Owner 的缺失契约。


# 附录 C：参考规范

1. RFC 2119 — https://www.rfc-editor.org/rfc/rfc2119
2. RFC 8174 — https://www.rfc-editor.org/rfc/rfc8174
3. CUE Language Specification — https://cuelang.org/docs/reference/spec/
4. Temporal Workflow Definition — https://docs.temporal.io/workflow-definition
5. Temporal Workflows — https://docs.temporal.io/workflows
6. Temporal Retry Policies — https://docs.temporal.io/encyclopedia/retry-policies
7. OpenAPI Specification — https://spec.openapis.org/oas/latest.html
8. AsyncAPI Specification — https://www.asyncapi.com/docs/concepts/asyncapi-document/structure


# 附录 D：对上一轮评审意见的逐项答复

| 评审意见 | 本规范答复 | 当前结论 |
|---|---|---|
| Observation ToolCatalog 表达不明确 | 提出在同一个 ToolCatalog 的 contracts 中使用 kind=operation / kind=observation 的类型化 callable；Observation 有独立 id、QueryContext Schema、Output Schema 和 guarantees | 方向已提出，字段仍待 Owner / Compiler 冻结 |
| Observation Query 调用语法不明确 | Operation 和 Observation Query 使用不同的 Procedure 节点关键字；精确身份由依赖快照解析，kind 由 ToolCatalog 决定；Query Input 使用具名 arguments 映射 | 语义已明确，正式 Schema / Fixture 待冻结 |
| Evidence 与 Predicate 参数的关联不明确 | Evidence 按业务参数分别关联；每个参数可无 Evidence、一个或多个 refs；input.evidence 是 Host 保留命名空间，业务参数 evidence 禁止 | 基数原则已明确；具体 Host Evidence Projection 和 Runtime 校验结构待 Owner 发布 |
| Predicate Script 类型派生不明确 | Predicate.parameters 是唯一业务输入签名；Script 入口 input: dict 仅为调用容器；Compiler / LSP 必须提供派生只读类型环境 | 语义已明确；生成 stub / overlay 的工具链方式待验证 |
| Schema ID 与路径混淆 | 外部引用使用 dependency-alias::精确 Schema $id；Skill 自有 Schema 使用包内路径；路径不是公共身份 | 规则已明确；需要 Compiler 正负例验证 |
| primitive 类型兼容、nullable 和 CEL 规则不完整 | 由 Compiler 类型兼容矩阵和正负例冻结，未支持关键字不得静默忽略 | 未冻结 |
| 自动同名绑定保留键冲突 | vNext 第一版不支持隐式同名绑定；Studio 可生成显式 arguments | 已纳入本版候选语法 |
| 三个异步 Operation 的 Owner 契约尚未确认 | 责任目标映射到 UPN.CREATE_UP_SESSION、SSM.SIGNAL_UE_AN、UPN.MODIFY_UP_SESSION | 仅为目标责任；ToolCatalog / Output / Evidence 仍待 Owner 确认 |

本附录是评审答复记录，不表示所有问题已实现或已冻结。评审者若不同意某项决定，应指出所影响的术语、语法、静态语义、运行语义或 Owner 边界，并提供正例和反例。

---

**规范结束。**
