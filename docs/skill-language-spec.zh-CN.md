# ConnectionAgent Skill Language Specification（CA-SL）

**中文名称：** ConnectionAgent Skill 语言规范  
**简称：** CA-SL  
**目标版本：** vNext / API v1alpha2  
**状态：** PUBLIC DESIGN REVIEW — NOT FROZEN  
**规范所有者：** odango-chan/ca-skills  
**消费者：** Skill 作者、Skill Studio、ca-skill-compiler、Agent Host / Runtime、Tool Owner、Schema Owner、语言服务和第三方评审者  
**更新日期：** 2026-11-14

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
3. 输入有来源：每个输入来自 Skill 自有 Schema、Owner Schema、Operation Result、Host Context 或显式 Observation Query。
4. 契约归属唯一：Schema 由真正拥有数据或接口的 Owner 发布；消费者不得复制并重新定义外部结构。
5. 权限可证明：Skill 授予 Capability；Procedure 调用精确 callable；部署侧 CapabilityContracts 定义 callable 归属和 Effect。
6. 观察与操作分离：Operation Result 与 Observation Result 保持不同语义；Observation 是受治理的只读查询能力。
7. Evidence 独立：Evidence 证明业务值的来源、主体、时间和相关性，不是业务 Payload 的替代品。
8. 不确定性显式：PASS、FAIL、UNKNOWN 不得混为一谈；Mutation 结果不确定时，按 §20 调和原操作或安全停止。
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

## 5. 源码与执行分层

1. **Skill 契约层：** 业务目标、公共 Request Schema、Context 要求、公共依赖和显式 Capability Grants，由 contract.yaml 声明；Skill 身份由 Package 路径确定。
2. **Procedure 层：** 单一确定性执行图，包含入口 Precondition、Operation / Observation、局部判断、最终 Postcondition、分支和终态。
3. **Predicate 层：** 可复用的纯判断定义；CEL 或受约束的 Python evaluator。
4. **Tool / Capability 层：** Owner 发布的 callable 契约、Schema、Effect，以及部署侧精确授权关系。
5. **Host / Runtime 层：** 执行隔离、Admission、Evidence、Correlation、Freshness、Deadline、Cancellation 和最终状态。

~~~text
Skill Package
 ├── SKILL.md
 ├── assurance/contract.yaml   # Goal / Request / Context / Dependencies / Capability Grants
 ├── assurance/procedure.yaml  # Procedure graph only
 ├── assurance/predicates.yaml
 ├── schemas/                  # Skill-owned Schemas only
 ├── scripts/                  # Skill-owned deterministic Scripts
 └── cases/ / references/
Compiler
 └── normalized Skill artifact / execution graph / generated Schemas
DependencySnapshot ── ToolCatalog + Owner Schemas
CapabilityContracts ── exact callable → Capability + Effect
Host / Runtime ── admission, execution, correlation, Evidence
~~~

## 6. 术语

### 6.1 Skill / Skill Package

Skill 是具有明确业务目标、输入契约、授权范围和执行入口的可复用业务能力包。Skill 不是 Tool；一个 Skill 可以调用多个 Tool，也可以被 Agent Router 选择。

vNext 作者维护的 Package：

~~~text
skills/<skill-name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/<case-name>/case.yaml
├── schemas/       # 仅 Skill 自有 Schema，例如公共 Request Schema
├── scripts/       # Skill 自有确定性 Python
└── references/    # 可选知识资料
~~~

| 资产 | 职责 |
|---|---|
| SKILL.md | 面向 Agent 的业务指导，不是第二份执行图 |
| contract.yaml | Skill 公共契约：Goal、Request Schema、Context 要求、公共依赖和 Capability Grants |
| procedure.yaml | 唯一 Procedure 执行图：start、节点、路由和最终 Postcondition |
| predicates.yaml | 可复用 Predicate 定义及其参数签名 |
| cases/ | 业务场景和预期语义义务 |
| schemas/ | 仅真正由 Skill 拥有的 Schema |
| scripts/ | Skill 自有确定性 Python；可作为 Procedure 的本地 Script Operation，也可实现 Predicate |
| references/ | 可选知识资料，不是执行契约或 Evidence |

vNext 保留作者维护的 assurance/contract.yaml，但不再使用重复的 apiVersion、kind、metadata 等机器对象包装。Contract 声明 Skill 的公共业务契约、依赖需求和 Capability Grants；Skill 身份从 Package 根目录确定。语言版本由 BuildRequest / Compiler Target 决定。外部依赖的具体内容由 Studio / 调用方通过 DependencySnapshot 提供，不复制到 Skill Package 的 lib/。

### 6.2 Goal、Request、Invocation 与编译契约

- **Goal：** Skill 希望达成的业务目标，由 contract.yaml 声明。`GoalId` 是非空、大小写敏感的字符串标识。Procedure 中的最终 Postcondition 以精确 GoalId 绑定该目标。
- **Request：** 调用方为本次执行提供的业务请求，由 contract.yaml 的 requestSchema 指向 Skill 自有 Schema；Request 本身不证明网络状态。
- **Context Schema：** Skill 通过 `contextSchema` 选择 Host Owner 发布的 Invocation Context Schema。Compiler 以该 Schema 校验 Host 字段路径。
- **Dependencies：** Skill 声明所需的公共 Owner 契约身份（例如 ToolCatalog、Host Context、Observation、共享 Schema）。声明依赖身份，不携带下载地址、版本锁或依赖内容。
- **Capability Grants：** Skill 在 contract.yaml 中显式声明所需 Capability 身份。Compiler 逐一验证每个外部 callable 都属于已 Grant 的 Capability；不得从“源码调用了某个 Tool”自动推导授权。
- **Skill Identity：** 由规范化 Package 根路径 / Package 名确定，不再要求作者在 YAML 重复填写 metadata.name。
- **Compiled Skill Contract：** Compiler 将 contract.yaml、Procedure 和 Predicate 定义归一化为 Runtime 所需的契约投影。它是派生产物，不是第二份作者源码；若 Runtime 不需要独立 Contract 文件，也不必单独输出。
- **Invocation：** 一次 Skill 独立执行实例。每次 Invocation MUST 有独立运行身份和隔离上下文。不得因为 UE 相同而共享未声明的可变状态。

### 6.3 Invocation Context

- **Context：** 本次 Invocation 对 Procedure 开放的已校验数据。Host 按 `contextSchema` 提供上下文对象，调用方的请求按 `requestSchema` 校验后通过 `context.request` 暴露。
- **UE Ref：** 本次业务执行的 UE 稳定引用，由 Host 解析并提供。
- **Correlation：** Host 接纳本次调用时确认的关联引用。5GC Invocation Context 包含 `correlation.ingressRef` 和 `correlation.lifecycleRef`。入口消息和原始 Evidence 由 Host 保管。

### 6.4 Procedure 与 Node

Procedure 是有向、确定性的执行图，定义输入、入口节点、动作、路由、恢复和终态。

Node 是图中的一个原子业务步骤，必须且只能声明一个主动作。Node 内不再嵌套隐式 Step，也不为每个 Operation 自动附加一套 Preconditions / Postconditions。需要判断时，显式使用 Precondition 或 Postcondition 节点。

Invocation 入口门禁允许先显式 Observation 再执行 Precondition。各成功分支可以执行各自的最终 Postcondition；局部 Precondition / Postcondition 仍可出现在图中间。具体规则见 §12.9。

### 6.5 Tool、Tool Operation 与 Operation Node

- **Tool：** 由 Owner 注册、实现并发布契约的外部能力单元，可由 HTTP Adapter、MCP、内建集成或其他受治理实现提供。Tool 是实现和契约发布单元，不是 Skill 授权身份。
- **Tool Operation：** Tool 提供的精确外部可调用业务接口，声明唯一 ID、Effect、Input Schema、Output Schema，以及对 Mutation 可选的 Reconcile Output Schema。它必须通过 CapabilityContracts 授权。
- **Operation Node：** Procedure 中执行一个业务动作的节点。其目标可以是一个外部 Tool Operation，也可以是 Skill 自有的纯 Procedure Script。前者受 READ / MUTATION Effect 和 Capability Admission 约束；后者是无外部副作用的本地计算，不是 Tool Operation，也不申请 Capability。
- **Operation Result：** 描述一次 Tool Operation 或本地 Script Operation 的规范化输出；必须保留其真实 Producer 身份，不能伪装成 Observation Result。

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
| 是否必然触发额外 Observation | 否，按 §12.6 判断结果是否充分 | 否，按 §12.6 判断是否还需其他事实 |
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

- **Script：** Skill Package 自有确定性 Python。Procedure Script 是 Operation 节点的纯本地数据转换/选择目标，Predicate Script 是 Predicate 的 evaluator；两者均非独立 Procedure 节点或外部 Tool / Capability。
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
| Invocation Context | Host / Context Owner | Skill 不得伪造可信上下文 |
| Evidence 记录和校验 | Evidence Producer + Host | Script 不得制造可信 Evidence |
| Capability 成员和授权 | Deployment Capability Owner | Skill 不得扩大授权 |
| 依赖获取和快照 | Skill Studio / 调用方 | Compiler 不得联网获取 |
| 静态解析和链接 | Compiler | Runtime 不得静默修补源码 |
| 外部副作用 | Tool / Provider / Adapter | Script 不得直接访问外部系统 |
| Deadline / Cancellation | Host / Runtime | Skill 不得定义任意轮询循环 |
| 真实网络状态 | 对应网元 / Owner | Skill 本地变量不是真相来源 |

## 8. Schema 所有权和身份

Skill 可以拥有公共 Request Schema 和真正属于 Skill 的业务结构，放在 schemas/。

Tool Owner 必须发布 callable 的 Input、Output，以及受支持的 Mutation Reconcile 契约及其可恢复输出 Schema。下游需要静态访问嵌套字段时，Owner 必须提供完整结构，不得长期用宽泛 object 掩盖缺失字段。

Observation Owner 发布 QueryContext / Input 和规范化 Output Schema。不得在 Skill Package 或平行 Observation Registry 中复制第二份。

Host Owner 发布 Invocation Context Schema。Contract 的 `contextSchema` 引用其精确 Schema ID，Procedure 在调用点显式绑定 `context` 路径。Compiler 检查依赖别名、可信快照身份、Owner、精确 Schema 和实际引用的字段。Host 按 §11.5 校验上下文并保留来源关联。

Script 输入和输出：
- Procedure Script 作为 Operation 节点的本地纯执行目标，输入由该节点 arguments 派生，输出 Schema 由严格返回 TypedDict 生成；
- Predicate Script 作为 Predicate evaluator，输入类型由 Predicate.parameters 派生，Host 附加只读 Evidence refs；
- Predicate Script 返回严格 PredicateEvaluationResult TypedDict，其中 result 为 PASS / FAIL / UNKNOWN，reasonCode 用于诊断，evidenceUsed 只能引用 Host 已附加的 Evidence；
- 作者不得维护重复 Script Input / Output Schema；
- Compiler 不得执行 Python 函数体猜测类型或行为。

必须区分物理路径、Schema 身份和 Dependency Alias。外部 Schema 使用：

~~~yaml
type: ca-context::urn:connectionagent:ca:context:invocation:v1
~~~

ca-context 是依赖别名，后半部分是 Owner 发布的精确 Schema $id。Skill 自有 Schema 使用包内路径：

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
          maxAgeMs: 10000
        evidence:
          correlation: required
          producerInvocation: required
          provides:
            - guarantee: smf.n4-resources
              path: output
~~~

kind 区分 operation 和 observation；id 在同一导出身份域中唯一；QueryContext Schema 不是 Operation Input Schema 的任意别名；Observation Output Schema 是 Owner 对外承诺的规范化结果；guarantees 是契约声明，Runtime 必须验证实际 Evidence；adapter 是 Owner 内部实现绑定，不是 Skill 源码身份。

不得通过通用 observation.read 和任意字符串 selector 暴露任意内部数据。最终字段、版本和兼容策略必须由 Tool Owner、Compiler 和 Runtime 评审，并通过正负例 Fixture 后冻结。

E.3 给出了带精确 Outcome 与 Evidence 描述符的独立 READ 样例。普通调用仅在 SUCCEEDED 边暴露成功输出。Reconcile 的路由和输出见 §12.7。

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

CapabilityContracts 使用稳定 Owner 身份 + 精确 callable ID + kind 标识成员，不得使用 BuildRequest 中临时的 Dependency Alias。Compiler 先通过 Skill 源码中的 Alias 找到 ToolCatalog，再以其 metadata.owner 和 callable 身份链接到 CapabilityContracts。Compiler 按 Owner、callable ID 和 kind 确定成员及其唯一 Capability，再比较两侧的 Effect；Skill 只能 grant Capability ID；缺失、重复或 Effect 不一致必须 fail-closed；Runtime 必须重新执行授权和 Effect Admission。该 YAML 是候选表达，必须与部署侧真实 CapabilityContracts 结构统一。

---

# 第四部分：源文件与 YAML 语法

## 10. 版本和文件

vNext 作者源码保留 contract.yaml、procedure.yaml 和 predicates.yaml 三个语义明确的入口文件。文件路径与所在目录决定源文件类型；这些文件不需要重复声明 apiVersion、kind 或 metadata 包装。

语言版本由 BuildRequest / Compiler Target 明确指定，而不是由每个 YAML 文件重复声明。Compiler 必须严格按指定版本解析；不支持的版本必须失败，不得猜测或兼容映射。编译产物记录实际采用的语言/API 版本、Skill Package 身份和生成器版本。

vNext 是破坏性版本。Compiler MUST NOT 静默把 v0.2 字段、旧路径或旧隐式输入模型转换为 vNext 语义。

当前仓库中的可执行 5GC Skill 仍有 v0.2 形态。本文示例说明目标语言，不代表旧文件已迁移或当前 Compiler 已支持。

## 10.1 YAML 语法子集与结构文法

CA-SL 使用 YAML 1.2 表达作者源码。YAML 是序列化格式，不是完整语言语义。Compiler MUST 使用安全解析器，并拒绝重复 Key、未知语义字段、非预期根类型、自定义 Tag、循环 Alias 和无法确定解释的标量。

vNext 源码由独立的 Skill Contract 和 Procedure 图组成：

~~~yaml
# assurance/contract.yaml
goal: pdu_session.initial_request_fulfilled
requestSchema: schemas/establishment-request.schema.yaml
contextSchema: ca-context::urn:connectionagent:ca:context:invocation:v1
dependencies:
  ca-context: urn:example:connectionagent:host-context
  ca: urn:example:connectionagent:5gc-tool-contracts
capabilities:
  - provider-5gc.session-read
  - provider-5gc.session-mutation
  - env-fabric.session-hold
  - ca-agent-host.session-runtime
~~~

~~~yaml
# assurance/procedure.yaml
start: observe-registration
nodes:
  observe-registration:
    observation: ca::ue.registration.current
    arguments:
      ueRef: context.ueRef
    'on':
      SUCCEEDED: check-registration
      FAILED: failed
      UNKNOWN: unresolved
  check-registration:
    precondition:
      entry: true
      predicate: createdsession.ue.registered
      arguments:
        - observe-registration.output
    'on':
      PASS: read-subscription
      FAIL: failed
      UNKNOWN: unresolved
  # 语法片段；完整 5GC Procedure 见 §30
~~~

规范性结构文法（抽象对象文法；map 表示 YAML 映射，字段 Schema 和静态语义另见 §11–14）：

~~~ebnf
Contract          = map(goal: GoalId,
                        requestSchema?: LocalSchemaPath,
                        contextSchema?: QualifiedSchemaId,
                        dependencies?: map<Alias, StablePackageId>,
                        capabilities?: list<CapabilityId>,
                        limits?: map(maxActions: PositiveInteger))
Procedure         = map(start: NodeId, nodes: map<NodeId, Node>)
Node              = PreNode | OperationNode | ObservationNode | PostNode | TerminalNode
OperationNode     = ToolNode | ScriptNode | ReconcileNode
PreNode           = map(precondition: map(predicate: PredicateId,
                            arguments: list<Expression>, entry?: true),
                        on: PredicateRoutes)
PostNode          = map(postcondition: map(predicate: PredicateId,
                            arguments: list<Expression>, goal?: GoalId),
                        on: PredicateRoutes)
ToolNode          = map(operation: QualifiedCallableId,
                        arguments: map<Name, Expression>, on: OperationRoutes)
ScriptNode        = map(operation: map(script: LocalScriptPath),
                        arguments: map<Name, Expression>, on: ScriptRoutes)
ObservationNode   = map(observation: QualifiedQueryId,
                        arguments: map<Name, Expression>, on: ObservationRoutes)
ReconcileNode     = map(operation: map(reconcile: OriginalMutationNodeId),
                        on: ReconcileRoutes)
TerminalNode      = map(terminal: TerminalStatus)
PredicateRoutes   = map(PASS: NodeId, FAIL: NodeId, UNKNOWN: NodeId)
ReconcileRoutes   = map(COMMITTED: NodeId, NOT_COMMITTED: NodeId, UNRESOLVED: NodeId)
TerminalStatus    = SUCCEEDED | FAILED | UNRESOLVED | SAFE_STOPPED
~~~

Node ID 与 `Identifier` 使用同一字符规则，并保留 `context`，避免 SourcePath 根歧义。Node 必须匹配其中恰好一种结构。Predicate 的 arguments 在 precondition / postcondition 对象内部；Tool / Script / Observation 的 arguments 位于 Node 顶层；on 在 Node 顶层。Terminal 不允许 on 或 arguments；Reconcile 不允许普通 arguments。OperationRoutes、ObservationRoutes 和 ScriptRoutes 的键集合由所链接的 Owner / Runtime 契约给出。Compiler 必须拒绝缺失或额外的 Outcome 路由。静态解析拒绝未知字段和多余主动作；编译器必须保留 YAML 标量的引号风格，才能区分 SourcePath 与字符串常量。

本版仅有单一 Procedure 图，不定义 entryProcedure、嵌套 ProcedureCall、通用 call、隐式 Step 或同名自动绑定。
## 11. Skill Contract 与 Procedure 源码

vNext 保留独立的 `assurance/contract.yaml`。它不是旧式带版本包装的 Kubernetes 风格资源对象，而是 Skill 的公共声明文件。它与 `procedure.yaml` 分工：

- Contract 声明 Skill 对外的业务目标、公共输入、Context 要求、公共依赖和 Capability Grants。
- Procedure 声明如何确定性地完成目标：start、四种业务节点、路由和最终 Postcondition。
- PredicateSet 声明可复用的判断定义和参数签名。

### 11.1 Contract 示例

~~~yaml
# assurance/contract.yaml
goal: pdu_session.initial_request_fulfilled

requestSchema: schemas/establishment-request.schema.yaml
contextSchema: ca-context::urn:connectionagent:ca:context:invocation:v1

# 仅声明稳定依赖身份；alias 是本 Skill 内部引用名。
# 不写 Git URL、版本锁、digest、分支或下载指令。
dependencies:
  ca-context: urn:example:connectionagent:host-context
  ca: urn:example:connectionagent:5gc-tool-contracts

capabilities:
  - provider-5gc.session-read
  - provider-5gc.session-mutation
  - env-fabric.session-hold
  - ca-agent-host.session-runtime
~~~

### 11.2 Procedure 示例

以下是独立的只读教学 Skill。其 Contract Goal 为 `udm.session_profile_verified`，完整 Contract 还需声明本例使用的 Request、Host Context Schema 和 READ Capability。它与 §11.1 的 PDU Session Skill 使用不同的 Contract。Predicate 签名见 §29。

~~~yaml
# assurance/procedure.yaml
# 配套 Contract 的 goal: udm.session_profile_verified
start: observe-registration
nodes:
  observe-registration:
    observation: ca::ue.registration.current
    arguments:
      ueRef: context.ueRef
    'on':
      SUCCEEDED: check-registration
      FAILED: failed
      UNKNOWN: unresolved

  check-registration:
    precondition:
      entry: true
      predicate: createdsession.ue.registered
      arguments:
        - observe-registration.output
    'on':
      PASS: read-subscription
      FAIL: failed
      UNKNOWN: unresolved

  read-subscription:
    operation: ca::sbi.udm.sm_data.get
    arguments:
      ueRef: context.ueRef
      dnn: context.request.dnn
      sNssai: context.request.sNssai
    'on':
      SUCCEEDED: verify-subscription
      FAILED: failed
      DENIED: failed
      UNKNOWN: unresolved

  verify-subscription:
    postcondition:
      goal: udm.session_profile_verified
      predicate: createdsession.udm.session_profile_usable
      arguments:
        - read-subscription.output.result
        - context.request.dnn
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

本例要求 Registration 查询输出与 §29 的 Registration 参数 Schema 匹配；UDM Get 的 output.result 与 Session Profile 参数 Schema 匹配。它是候选 Owner 契约下的说明性示例，而非当前已可链接的真实 5GC Skill。

### 11.3 Contract 字段

| 字段 | 语义 | 约束 |
|---|---|---|
| goal | Skill 的业务目标 | 必须声明；不等于某个 Operation 成功 |
| requestSchema | 公共 Request Schema | 有调用方 Request 时声明；指向 Skill 自有 `schemas/` 文件 |
| contextSchema | Host 提供的 Invocation Context | 引用已声明依赖别名的精确 Owner Schema ID；使用 Host Context 字段时必须声明 |
| dependencies | 公共依赖声明 | Alias → 精确稳定 Package ID，必须与可信调用方提供的快照身份绑定核对；不声明 URL、digest 或获取方式 |
| capabilities | Skill 请求的授权上界 | 只列 Capability ID；Compiler 对每个外部 callable 做精确 membership / Effect 校验 |
| limits.maxActions | 可选的 Skill 业务动作预算上界 | 正整数；Host 的实际预算只可进一步收紧，不能被该字段放宽 |

### 11.4 字段归属与省略规则

- `apiVersion`、`kind`：Skill 的 `contract.yaml`、`procedure.yaml`、`predicates.yaml` 省略这些包装。ToolCatalog 和 CapabilityContracts 是独立发布的资源，按各自契约声明版本。语言版本由 BuildRequest / Compiler Target 决定；文件路径和内容结构决定源文件类型。
- `metadata.name`：由 Skill Package 根目录确定，不重复维护。
- `skillType`：vNext Skill 都使用统一执行模型；除非未来出现有实质语义差异的 Skill 类型，否则不作为必填字段。
- `entryProcedure`：每个 Skill 只有一张入口 Procedure 图，入口由唯一 `procedure.yaml` 确定。
- `postconditions`：不在 Contract 重复声明。最终 Postcondition 是 Procedure 图中的真实节点，具有显式 arguments、执行位置、Evidence lineage 和 PASS / FAIL / UNKNOWN 路由。
- `inputs`、`context.requiredFacts`、`context.schemas`：旧包装与拆分声明。公共请求和 Host 上下文分别通过顶层 `requestSchema`、`contextSchema` 声明，字段必需性由对应 Schema 和 Host 准入规则约束。
- `evidenceSchema`：通用 Evidence Envelope 由 Host / Runtime 统一定义和校验，不由 Skill 重复声明。
- `planning.allowDynamicProcedure`：不再需要。vNext Procedure 是静态 DAG，动态生成执行图不属于语言能力。
- `planning.maxActions`：旧名称删除。若 Skill 需要明确的业务动作上界，可在 Contract 中声明可选 `limits.maxActions`，与 Host / Deployment 的强制预算取较小值。
- `failureSemantics.outcomeUnknown.requireReconcile`：Mutation UNKNOWN 的通用安全规则见 §20。只有具备可安全执行的 Owner 契约时才调和原操作；否则停止并保留不确定状态。

Contract 中的依赖身份与 Capability Grants 是两件不同的事：Dependency 让 Compiler / Studio 获得并链接 Owner 契约；Capability Grant 才表达 Skill 被允许请求的业务能力。依赖存在不等于获得执行权限，Grant 也不能替代 ToolCatalog / Schema 依赖。

Skill Studio 创建 Skill 时应让作者从可用的公共依赖目录和可信 CapabilityContracts 中选择依赖与授权，再将稳定身份写入 `contract.yaml`。Studio 负责获取所选依赖的确切快照并把字节交给 Compiler；Compiler 只校验和链接，不联网解析、不下载依赖，也不管理版本锁。依赖快照 / 版本选择属于 Studio 项目配置或 Build 输入，不属于 Skill 公共 Contract。Owner Schema ID 如果自身包含不可变版本标识（例如 `...:v1`），该身份仍必须原样保留；这与在 Contract 顶层重复声明 `apiVersion` 不同。

### 11.5 Contract 与 Invocation Context

- `requestSchema` 指向 Skill 自有请求 Schema，约束 `context.request` 及其子路径。`contextSchema` 引用已声明依赖别名下 Host Owner 发布的精确对象 Schema ID，约束 `context` 下其余字段。`request` 为保留属性，Host Schema 不得声明该属性或用开放的字段规则接纳它。引用路径必须由对应 Schema 显式定义，缺少声明或字段时阻断构建。
- Host 在完成入口准入后物化当前 Invocation 的上下文，保留字段的 Schema 与来源关联。Runtime 分别校验已声明的 Host 对象和调用方请求，校验通过后将它们作为本次 Invocation 的只读值开放给 Procedure。对于引用的路径，Compiler 检查字段存在性、可选性、可空性和类型。调用点只能获得显式绑定的数据。
- 传统 5GC 使用 `ca-context::urn:connectionagent:ca:context:invocation:v1`。Host Schema 要求 `ueRef` 和 `correlation`，后者要求 `ingressRef`、`lifecycleRef`。Host 在准入时验证这些值属于本次调用，包含精确的已接纳入口引用和独立解析的生命周期绑定。Schema 的字段校验和 Host 的关联校验都必须通过。实时网络状态来自显式 Observation 或具有充分 Evidence 的 Operation Result。
- Compiler 独立检查依赖、Schema 与 Capability Grants。依赖用于链接 Owner 契约，外部调用还必须通过 §9.3 的 Capability 校验。

### 11.6 动作预算

`limits.maxActions` 可省略；省略时采用 Runtime 提供的强制预算。若声明，必须是大于 0 的整数；定义一次 Action 为一次实际派发的外部 Operation、Observation、Procedure Script 或 Reconcile（包括失败或 UNKNOWN 的尝试）。Predicate / Terminal 不计 Action，但仍消耗 Runtime 的总节点和时间预算。有效上限为 Skill 上界与 Host 上界的较小值；Host 预算缺失、不合法或为 0 时 Admission 必须 fail-closed。该字段不影响 Capability Grant，不提供额外重试权限，也不能覆盖 Runtime 的 Deadline / Cancellation。

vNext 不允许直接把 Operation ID 放入 Capability 授权列表，不允许 localTools，不允许把 Host 内部 dataclass 路径写入 Skill，不允许推断未发布的 Context 字段，也不允许使用物理 lib 路径充当公共依赖身份。

## 12. Procedure

### 12.1 核心结构

Procedure 是确定性的有向执行图。每个 Node 必须且只能声明一个主动作。vNext 的业务节点只有四种：

1. precondition：调用 Predicate 判断执行前置条件；
2. operation：调用 Owner Tool Operation、执行 Skill 自有的纯 Script，或按 Owner 契约调和本次已派发的 Mutation（§12.7）；
3. observation：调用 ToolCatalog 中的只读 Observation Query；
4. postcondition：调用 Predicate 判断执行结果。

terminal 是显式终态声明，不是业务动作。Predicate、CEL 和 Python Script 都不是独立 Procedure 节点；Predicate Script 是 Predicate 的 evaluator，Procedure Script 是 Operation 节点的本地执行目标。

下例假定 Create 的 Owner 契约声明 SUCCEEDED、NOT_COMMITTED、OUTCOME_UNKNOWN、DENIED、FAILED。实际节点的路由键按所链接的契约填写（§22）。

~~~yaml
# assurance/procedure.yaml：独立教学 Skill，Contract Goal 为 udm.subscription_verified
start: create-subscription
nodes:
  create-subscription:
    operation: ca::sbi.udm.sdm_subscription.create
    arguments:
      ueRef: context.ueRef
      dnn: context.request.dnn
    'on':
      SUCCEEDED: verify-direct
      NOT_COMMITTED: failed
      OUTCOME_UNKNOWN: reconcile-subscription
      DENIED: failed
      FAILED: failed

  # 已收到有充分 Evidence 的成功结果：不重复 Observation
  verify-direct:
    postcondition:
      goal: udm.subscription_verified
      predicate: createdsession.udm.subscription_usable
      arguments:
        - create-subscription.output.subscription
        - context.request.dnn
    'on':
      PASS: complete
      FAIL: safe-stopped
      UNKNOWN: safe-stopped

  reconcile-subscription:
    operation:
      reconcile: create-subscription
    'on':
      COMMITTED: inspect-after-reconcile
      NOT_COMMITTED: failed
      UNRESOLVED: unresolved

  # 原响应丢失：调和契约只恢复精确资源 Ref，查询该 Ref 的当前状态。
  inspect-after-reconcile:
    observation: ca::udm.subscription.current
    arguments:
      ueRef: context.ueRef
      subscriptionRef: reconcile-subscription.output.subscriptionRef
    'on':
      SUCCEEDED: verify-reconciled
      FAILED: safe-stopped
      UNKNOWN: safe-stopped

  verify-reconciled:
    postcondition:
      goal: udm.subscription_verified
      predicate: createdsession.udm.subscription_usable
      arguments:
        - inspect-after-reconcile.output.subscription
        - context.request.dnn
    'on':
      PASS: complete
      FAIL: safe-stopped
      UNKNOWN: safe-stopped

  complete:
    terminal: SUCCEEDED
  failed:
    terminal: FAILED
  unresolved:
    terminal: UNRESOLVED
  safe-stopped:
    terminal: SAFE_STOPPED
~~~

本例使用独立 Contract `goal: udm.subscription_verified`，并假设 Host 在派发前登记对创建尝试和迟到结果的责任。成功完成后该订阅由已登记的管理方接管。提交后的验证失败进入 SAFE_STOPPED。Tool Owner 须明确保证 Create 成功输出和独立 Observation 输出中的 subscription 均符合相同规范化 Subscription Schema，并发布相同权威的订阅状态保证（§17）；该假设须由正式 Owner Schema 确认，不能靠 Compiler 猜测。COMMITTED 只证明原 Mutation 已提交。本例另假设调和契约为 COMMITTED 声明并保证恢复精确 `subscriptionRef`；它从 Reconcile 自身输出取得。只按 UE 或 DNN 查询其他订阅不能证明本次创建。两条成功路径分别通过标记同一 Goal 的 Postcondition PASS，直接进入共享 Terminal。

### 12.2 Precondition

Precondition 在受保护的业务动作之前执行 Predicate。它可以检查 Host Context、Request、此前 Operation Result 或 Observation Result。Precondition 不得隐式查询外部系统；若缺少事实，应先通过显式 Observation 获取，再调用 Predicate。

~~~yaml
check-ue-registration:
  precondition:
    entry: true
    predicate: createdsession.ue.registered
    arguments:
      - observe-ue-registration.output
  'on':
    PASS: create-session
    FAIL: reject-request
    UNKNOWN: unresolved
~~~

本片段引用 §30 的 Registration Observation 输出和 §29 的 Registration Schema。Precondition 必须为 PASS、FAIL、UNKNOWN 分别声明路由。两条边可以指向同一处理节点；Trace 和终态判定仍保留各自的原始 Outcome。

### 12.3 Operation

Operation Node 表示一个业务动作。若目标是外部 Tool Operation，其精确 callable 身份、Effect、Input / Output Schema 和必要的 Reconcile 契约由 Tool Owner 在 ToolCatalog 中发布；若目标是本地 Script，则按 §32 的纯计算约束执行，不属于 ToolCatalog 或 Capability 授权体系。

~~~yaml
create-policy:
  operation: ca::sbi.pcf.sm_policy.create
  arguments:
    ueRef: context.ueRef
    pduSessionId: context.request.pduSessionId
    dnn: context.request.dnn
    sNssai: context.request.sNssai
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
  observation: ca::pcf.policy_association.current
  arguments:
    ueRef: context.ueRef
    pduSessionId: context.request.pduSessionId
  'on':
    SUCCEEDED: verify-policy
    FAILED: failed
    UNKNOWN: unresolved
~~~

Observation 的 arguments 同样是具名映射，并按 Query Input Schema 校验。Observation Query 可以使用前序 Operation Result 作为查询依据，例如：

~~~yaml
inspect-n4-resources:
  observation: ca::smf.session.n4_resources
  arguments:
    phase: "POST_CREATE"
    sessionInstanceRef: create-n4-session.output.sessionInstanceRef
    baselineRef: read-n4-baseline.output.baselineRef
~~~

这里 Operation Result 只提供查询目标和关联身份；Observation 必须由其权威 Owner 实际执行查询并返回自己的 Result / Evidence，不得把 Operation Result 包装或改名成 Observation Result。

### 12.5 Postcondition

Postcondition 调用 Predicate 判断业务结果是否成立。其参数可以来自 Operation Result、Observation Result、Invocation Context 或多个来源的组合。

~~~yaml
verify-n4-session:
  postcondition:
    predicate: createdsession.n4.initial_resources_ready
    arguments:
      - inspect-n4-resources.output
      - read-n4-baseline.output.baselineRef
  'on':
    PASS: next-step
    FAIL: failed
    UNKNOWN: unresolved
~~~

本片段假设前序 `read-n4-baseline` 在 PRE_CREATE 阶段成功产生已确认的 `baselineRef`，且该输出在所有到达路径上可用。POST_CREATE 查询与 Predicate 均绑定同一 Ref；`inspect-n4-resources.output` 使用 §29 所示的权威输出类型。

如果 Operation Result 已包含满足 Predicate 所需的事实、Scope、Correlation、Freshness 和 Evidence，可以直接作为 Postcondition 输入，不需要 Observation。

### 12.6 Operation Result 充分性原则

**Result Sufficiency Principle（结果充分性原则）：** Procedure MUST 优先复用已有且满足当前判断要求的 Operation Result、Context 和 Evidence。只有当现有信息不足以支持目标 Predicate，或业务规则明确要求独立权威观察时，才执行 Observation。

- Operation Result 已满足业务判断和 Evidence 要求时，不得为了形式上的配对增加重复 Observation。
- Operation Result 只证明请求已接受、未证明目标状态时，应根据业务需要执行 Observation 或等待由 Operation Owner 提供最终完成结果。
- Postcondition 可以同时接收 Operation Result 和 Observation Result，以验证二者之间的一致性。
- Operation 与 Observation 必须保留真实 Producer 身份；不得将 Operation Result 伪装成 Observation Result。
- Observation 的 Freshness 和 Scope 必须满足当前 Predicate 要求；“曾经观察到”不等于“当前仍成立”。

### 12.7 Reconcile

Reconcile 是 Operation 节点的一种形态，用于调和已经派发的 Mutation。它必须指向本次 Procedure 中一个已执行的原始 Mutation Node：

~~~yaml
reconcile-policy:
  operation:
    reconcile: create-policy
  'on':
    COMMITTED: next-step
    NOT_COMMITTED: failed
    UNRESOLVED: safe-stopped
~~~

Runtime 必须使用原始 Mutation 的不可变 Invocation、Operation 身份、输入、Scope 和 Correlation 执行对应 Owner 契约的 Reconcile。Reconcile 不得变成新的 Create / Update 请求，不得接受另一组业务参数来改变原操作目标。Compiler 必须验证目标存在、目标确为 MUTATION 且发布了安全 Reconcile 契约。到达 Reconcile 的每条路径均须经过该目标的 `OUTCOME_UNKNOWN` 边，且该次尝试尚未调和。Compiler 将 `reconcile-node.output` 链接到原 Mutation Owner 契约声明的 **Reconcile Output Schema**。该 Schema 只在 COMMITTED 边提供，形状可与原 Mutation 的成功输出不同。Owner 未声明恢复输出时，COMMITTED 边不提供 `output`，后续可显式读取权威状态。承诺的输出未通过校验时按 §20.2 停止。示例假定此前有部分资源需要保全，因此 UNRESOLVED 边指向 SAFE_STOPPED。

### 12.8 Terminal 与 Applicability

Terminal 显式声明 `SUCCEEDED`、`FAILED`、`UNRESOLVED` 或 `SAFE_STOPPED`。Runtime 根据已确认的执行状态发布终态；声明为 SUCCEEDED 仍须通过 §12.9 的检查。没有匹配路由或未识别 Outcome 时，先按 §20 确定已派发 Mutation 的已知状态，再记录异常并按以下规则结束。

- SUCCEEDED：实际路径有有效 Goal PASS，所有 Mutation 提交状态均已确定，已确认资源及迟到结果均有明确责任。
- 需要停止时，依次检查：① 有已知部分完成资源或已确认的外部变更需要保全、核实或处置，发布 SAFE_STOPPED；② 否则，关键事实或已派发调用的提交状态仍不确定，发布 UNRESOLVED；③ 其余停止情况发布 FAILED。一个停止同时存在已知部分完成和未知提交时优先 SAFE_STOPPED，原因仍记录为不确定。
- 显式停止 Terminal 表达作者对该路径的预期。Runtime 始终按上述顺序计算发布值。无第 ①、② 项且流程已经选择停止时，发布 FAILED；保留原停止原因。发布值与声明不同，记录 `TERMINAL_STATE_MISMATCH`。例如，声明 UNRESOLVED 但已确定失败且无部分完成时发布 FAILED；声明 FAILED 但有资源待保全时发布 SAFE_STOPPED。门禁失效、全局限制或 Reconcile 无法派发时也使用同一规则；普通调用的派发前拒绝见 §24.2。

Host 在派发 Mutation 前记录原调用身份和负责处理结果的 Owner / 责任引用。终态按发布时已接纳的状态判定；迟到结果由已登记责任方继续处理，并追加到责任记录。停止时持久化已有资源句柄、责任引用、未决调用与停止原因；即使没有已知资源，未知尝试的迟到结果责任也必须保留。后续清理或移交由已授权的 Owner 负责。

Skill Eligibility 属于 Root Routing / Host 准入。无法唯一匹配时不得随机选择或默认执行。Procedure Predicate 负责业务条件，不负责猜测 Skill 身份。完整 Applicability YAML 语法需要与 Root Routing 契约统一冻结；历史 applicability.when 不作为隐式兼容语法。

### 12.9 Procedure 入口、最终门禁与控制流

- Invocation 入口 Precondition 用 `precondition.entry: true` 标记。可以先执行显式 Observation 获取事实，再执行一个或多个入口 Precondition。从 start 到每个业务 Mutation 的每条路径都必须经过**每一个** `entry: true` 节点的 PASS 边，Compiler 逐路径检查。入口 FAIL 或 UNKNOWN 可以在 Mutation 前结束流程。没有 Invocation 级门禁时省略标记；局部门禁由 Procedure 的显式路由表达。
- 每次业务 Mutation 派发前，Runtime 以当前 Scope 和校验时间复核本 Invocation 中全部入口 PASS 的原绑定及所需 Evidence（§17.2）。过期、被取代、关联失效或冲突时，所需事实在派发点未获充分证明，不派发 Mutation，记录 `ENTRY_PRECONDITION_INVALIDATED`（仅局部门禁失效时为 `PRECONDITION_INVALIDATED`），并按 §12.8 停止。Runtime 不重新执行 Predicate，不隐式查询或刷新；会变化且需要刷新以继续执行的条件，应建模为紧邻受保护动作的局部 Observation / Precondition；Invocation 级入口门禁用于整个 Invocation 都必须持续成立的条件；非入口 Precondition 或局部 Postcondition 的 PASS 直接连到 Mutation 时，Runtime 把该 PASS 作为本次派发的局部门禁并复核。中间隔有其他节点时，该 PASS 只决定路由。若需要派发前复核，应将相应判断放在 Mutation 的直接前驱。Reconcile 按原调用及 §20 独立准入，业务门禁证据过期本身不阻止对原调用的安全调和。
- 最终 Postcondition 用 `postcondition.goal` 标记，值必须精确等于 `contract.yaml` 的 `goal`。`start` 可以指向这一种节点，例如只判断本次 Invocation 已准入的数据。到达 `start` 时尚无证明，该节点自己的 PASS 出边可以建立证明。节点只能匹配一种文法结构；入口 Precondition 与 Goal Postcondition 需要分别声明。局部 Postcondition 省略 `goal`，其 PASS 不能建立最终证明。该标记只声明节点证明哪个 Goal；Predicate 和 arguments 仍由节点声明，Contract 无须重复列 Predicate 或绑定。
- 对每个从 start 可达的 SUCCEEDED Terminal，每条控制流路径都必须有一条匹配 Goal 的 Postcondition PASS 边，且该边之后只经过非入口 Precondition 的 PASS、无 `goal` 的 Postcondition 的 PASS，或 READ / Observation / Procedure Script 的 SUCCEEDED。这些出边只传递已有证明。入口 Precondition 的 PASS 清除已有证明，使最终验收发生在入口门禁之后。出现新的匹配 Goal PASS 时，以新判定为准；Mutation、Reconcile 或任何非成功边使已有证明失效。不同路径可由不同节点证明同一个 Goal，也可共享 Terminal。若可达 SUCCEEDED 且没有任何可达的匹配 Goal 节点，报告 `FINAL_POSTCONDITION_MISSING`；否则按以下规则检查绕过路径。
- Runtime 沿本次实际执行的线性轨迹维护 Goal 判定，按边的执行顺序更新或清除。到达 SUCCEEDED 时只复核当前保存的 Goal PASS，检查其输入 lineage、Evidence 有效性和资源责任。若该判定过期、被取代或关联失效，视为 Goal 未获得充分证明，不得回退到更早的 PASS；资源状态或责任不明时，也按 §12.8 停止并记录原因。该检查复用本次判定及其证据，不再次调用 Predicate 或隐式查询外部系统。Compiler 验证标记、绑定与路径；Goal 与 Predicate 的业务含义是否相符由 Skill / 业务 Owner 评审。
- 每个 SourcePath 的 Producer Output 必须在所有到达消费点的路径上实际可用。Compiler 从发布的 Outcome 契约判断输出可用性；普通成功输出只在 SUCCEEDED 边产生，Reconcile 的 COMMITTED 输出按 §12.7。运行时无效输出按 §20、§24.2 停止或路由，不进入要求该输出的成功边。
- 第一版 Procedure 为 DAG，无隐式循环或任意 back-edge，每个 Skill 只有一张入口图。只有 §20 允许的受控新尝试可以用另一个显式 Operation 节点表达，并受 Deadline / Budget 限制。复用纯判断使用 Predicate，复用纯数据转换使用 Script。

Compiler 按拓扑顺序处理从 start 可达的节点。`hasProof` 表示到达该节点的所有路径都持有结构上有效的 Goal PASS。汇合时只对源节点从 start 可达的入边取 AND，入边各自保留其 Outcome。来自不可达节点的入边不参与证明传播。Compiler 对不可达节点另报 `UNREACHABLE_NODE` 警告。可达的成功 Terminal 无有效证明时报告 `SUCCESS_BYPASSES_FINAL_POSTCONDITION`，缺少可达 Goal 节点时优先报告 `FINAL_POSTCONDITION_MISSING`。

~~~text
for node in reachable_nodes_in_topological_order:
    hasProof = false if node == start else AND(reachable_incoming_edge_proofs)
    if node.terminal == SUCCEEDED and not hasProof:
        reject success path
    for edge in node.outgoing_edges:
        if edge is a matching Goal Postcondition PASS:
            edge.proof = true
        else if edge is PASS from a Precondition without entry: true:
            edge.proof = hasProof
        else if edge is PASS from a Postcondition without goal:
            edge.proof = hasProof
        else if edge is SUCCEEDED from a READ Operation, Observation, or Procedure Script:
            edge.proof = hasProof
        else:
            edge.proof = false
~~~

## 13. Arguments 与数据来源

### 13.1 统一表达

vNext 删除 Procedure Node 上的 `with` / `from` / `value` 包装，统一使用直接表达式：

- Tool Operation.arguments：具名映射，键为 Owner Input Schema 字段；Procedure Script Operation.arguments：具名映射，作为该次 Script 调用的完整输入投影；
- Observation.arguments：具名映射，键为 Query Input Schema 字段，值为来源表达式或标量字面量；
- Precondition / Postcondition.arguments：有序列表，位置与 Predicate.parameters 严格对应。

~~~yaml
# assurance/procedure.yaml 的语法片段；Goal/授权属于 contract.yaml
start: create-session
nodes:
  create-session:
    operation: ca::smf.session.create
    arguments:
      ueRef: context.ueRef
      dnn: context.request.dnn
    'on':
      SUCCEEDED: verify-session
      FAILED: failed
~~~

该片段仅示范参数表达，不是完整可执行图：所有跳转目标以及最终 Postcondition / Terminal 必须在完整源文件中定义。

### 13.2 参数表达式与 SourcePath

- `arguments` 映射的每个值和列表的每个元素都是 Expression。使用 YAML 1.2 Core 标量规则，并保留标量是否加引号。裸字符串仅在匹配 SourcePath 文法时合法；字符串常量须加引号。例如 context.ueRef、context.request.dnn、read-subscription.output.result、read-subscription.output.result.subscription.dnn。
- YAML 原生 Boolean、Number、Null 和带引号的 String 表示字面量。例如 `phase: "POST_CREATE"` 是合法字符串常量，`phase: POST_CREATE` 报 `SOURCE_PATH_INVALID`。`baselineRef: read-n4-baseline.output.baselineRef` 是来源引用。
- vNext 第一版不允许在 arguments 中内联任意对象或数组字面量；复杂对象必须来自一个有 Schema 的 Request、Context 或 Producer Output。`context` 路径读取 §11.5 已校验的 Invocation 值。节点输出路径只能读取当前执行路径上已产生的有效输出。
- Predicate.arguments 必须是有序列表，位置与 Predicate.parameters 严格对应。
- Tool Operation、Procedure Script Operation 和 Observation.arguments 必须是具名映射。Tool / Observation 的键由 Owner Schema 定义；Procedure Script 的键构成该次 Script 调用的精确输入投影。
- Reconcile 不接受 arguments；其唯一输入是被引用的原始 Mutation Invocation。

抽象 SourcePath 文法：

~~~ebnf
SourcePath          = ContextPath | ProducerOutputPath ;
ContextPath         = "context", ".", Identifier, { ".", Identifier } ;
ProducerOutputPath  = NodeId, ".output", { ".", Identifier } ;
Identifier          = Letter, { Letter | Digit | "_" | "-" } ;
~~~

SourcePath 只能引用已声明的 Invocation Context 或一个已执行 Producer Node 的 output。不得引用父 Procedure 隐式变量、全局变量、其他 Invocation、Runtime 私有字段或未声明的环境变量。

vNext 第一版只支持静态点路径，不支持数组索引、动态下标、字符串插值、函数调用、通配符或运行时路径拼接。Owner Schema 中需要被 Skill 直接访问的字段必须使用可由 Identifier 表达的字段名；不符合该规则的外部字段应由 Owner 在规范化输出中提供稳定字段名。
### 13.3 静态校验

Compiler 必须验证：
- 参数名在目标 Schema 中存在；
- 所有 Required 参数均提供；
- 不得传入未声明字段；
- SourcePath 必须在每条可达路径上存在。Compiler 先解析 Producer 与其输出 Schema，再检查路径和 Outcome，最后检查类型可赋值性。路径某段未在对应 Schema 中声明时报告 `SOURCE_PATH_INVALID`。已声明的路径因当前分支没有相应 Producer Outcome 而不可用时报告 `SOURCE_NOT_AVAILABLE`；引用 Owner 未声明的 Reconcile 输出时按 §12.7 报 `RECONCILE_OUTPUT_UNAVAILABLE`。若属性在该 Outcome 的 Schema 中可缺失（包括 TypedDict 的 `NotRequired`），直接取该属性的路径报告 `SOURCE_NOT_AVAILABLE`。可绑定保证存在的外层对象，再由消费者按其 Schema 处理可选成员。Predicate PASS 本身不缩窄后续 SourcePath 类型。例如局部门禁确认 `read-policy.output` 中的可选 `policyRef` 有值，即使 PASS 边直接连到 Mutation，其 `arguments.policyRef: read-policy.output.policyRef` 仍报 `SOURCE_NOT_AVAILABLE`；
- Source Schema 可赋给目标字段 Schema；
- Optional、Nullability、enum、const、范围和数组元素约束兼容；
- 来源的 Subject、Session、Lifecycle 和 Evidence Scope 没有被不安全地扩大；
- Reconcile 不接受普通 arguments，而引用原始 Mutation Invocation。

### 13.4 最小输入与无隐式转发

只传递目标契约实际需要的字段。不得自动转发调用方全部字段，不得从父 Procedure、Context 或上一个 Node 猜字段，不得根据字段同名自动绑定。目标 Schema 的可选参数可以省略。省略与显式 null 分别校验。Compiler 不从 JSON Schema 的 default 合成参数。

Skill Studio 可以通过语义身份和 Schema 提供参数补全、批量生成显式映射，但保存后的源码必须完整呈现最终参数映射。

## 14. PredicateSet

~~~yaml
predicates:
  createdsession.udm.subscription_usable:
    parameters:
      - subscription: ca::urn:connectionagent:5gc:tool-output:udm-subscription-result:v1
      - requestedDnn: string
    evidence:
      requires:
        subscription: [ca::udm.subscription-state]
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
- Predicate 签名是唯一业务输入契约；`evidence` 是独立的来源要求，字段和校验见 §17。

当前 Evaluator 支持 CEL 和 Skill 自有 Script。Predicate 不得调用 Tool、Observation、网络、文件系统、时钟、随机数或全局 Context，也不得修改外部状态。

结果：
- PASS：输入和 Evidence 足以支持命题成立；
- FAIL：输入和 Evidence 足以支持命题不成立；
- UNKNOWN：无法可靠判断。

UNKNOWN 不是 FAIL 的别名，也不是“先通过再说”。Evidence 缺失、冲突、过期、Scope 不匹配或来源不可信时，不得接受没有依据的 PASS。

CEL 的布尔 `true` / `false` 分别产生 PASS / FAIL。静态可知的非布尔表达式阻断构建；求值异常、未绑定值或无法得出布尔结果时走 UNKNOWN。Script 返回不符合结果契约或抛出求值异常时也走 UNKNOWN；Host 级取消与执行截止按 §24.2 停止。

初始 Primitive：string、integer、number、boolean。结构化对象和数组使用 Schema 引用。Compiler 必须逐个绑定点检查 Source Schema 是否可赋给 Target Schema，并覆盖 integer / number、enum / const、required / optional、nullable / omitted、additionalProperties、数组元素、范围约束和组合 Schema。未支持的 Schema 关键字不得静默忽略；最终兼容矩阵需通过正负例冻结。

---

# 第五部分：Observation 与 Evidence


## 15. Observation Query 调用时机

仅在以下情况执行 Observation Query：
1. Invocation 缺少所需事实；
2. 前序 Operation Result 没有提供该事实；
3. Host Context 不足以满足 Scope / Freshness / Authority；
4. 必须向事实 Owner 查询当前状态；
5. 业务规则要求独立核实。

不应增加 Observation Query：
- 前序 Operation Result 已提供精确值和充分 Evidence；
- Host Context 已是 Host 信任的权威输入；
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

Freshness 由 Owner Contract 声明可执行的有效性规则（例如从 observedAt 计时的最大时长）并由 Runtime 验证。旧事件、错误 Lifecycle、错误 Correlation 或过期结果不能证明当前状态。

## 17. Evidence 与 Predicate 参数

### 17.1 业务签名与来源要求

Predicate 的 `parameters` 声明业务值类型。`evidence.requires` 可选，是参数名到一组非空、无重复的精确 `alias::guaranteeId` 的映射；只允许引用已声明参数。每个列出的保证至少由一条有效 Evidence Ref 满足，列表全部满足才成立。需要独立证据时，引用不同保证并用 Owner 声明的独立来源约束校验，见 §17.2。省略参数表示它不额外要求 Evidence，例如字面量、请求 DNN 或作为比对目标的已验证请求字段。用于证明外部状态的参数必须声明对应保证；纯本地判断和请求形状判断可以省略。Compiler 检查声明的要求和来源，业务 Owner 评审外部状态判断所需的保证是否齐全。

保证引用解析到可信 Owner 契约中的唯一精确身份。可执行描述符至少给出权威 Owner、允许的 Producer 身份及值路径、适用的 Scope / Correlation 维度及其与当前 Invocation 或已校验调用参数的取值绑定、同一事实的记录选择规则，以及 Freshness 的时间基准和判定规则。Predicate 参数 Schema 由 `parameters` 声明。Producer 值的 Schema 从已发布的输出或 Host Context Schema 按值路径解析，并对参数 Schema 检查可赋值性。`provides[].guarantee` 是该发布方快照中精确的描述符导出键，可以指向同一快照内的独立契约。Compiler 必须解析到唯一导出，并核对描述符允许的 Producer 身份、Outcome 与 `provides[].path`；`output` 指整个已声明的输出。缺失、歧义或路径不匹配均拒绝链接。声明的 `provides` 引用解析失败时报告 `EVIDENCE_GUARANTEE_LINK_INVALID`。E.3 示范分文件声明。Operation Result 和 Observation Result 可提供同一个保证，前提是该权威 Owner 明确授权两条 Producer 路径。Skill 只引用保证 ID；Schema、Owner、相关性和有效期由 Owner 契约提供。描述符中，Observation Producer 的实参引用根为 `query`，Operation Producer 的实参引用根为 `arguments`。两者是保留根，指向相应 Producer 派发时物化并通过校验的实参。Compiler 按描述符中的 Producer kind 校验引用根与字段路径，未知根、根与 kind 不符或实参路径无法解析时报 `EVIDENCE_GUARANTEE_LINK_INVALID`。描述符的传输格式仍待联调。

### 17.2 静态绑定与运行校验

1. Compiler 先检查参数数量和各 SourcePath 的可用性，再检查 Schema 可赋值性和 Evidence 要求。Producer 身份及精确值路径由 SourcePath 解析确定。每条可达路径必须提供所需保证及可解析的 Scope、Correlation 和 Freshness 规则。精确投影只保留 Owner 明确覆盖的证据。Procedure Script 的计算结果不能继承输入的权威 Evidence；派生值须由 Host 契约另行提供可验证的关联。
2. Runtime 固定本次校验时间与 Invocation 已接纳记录的视图。前置复核与后续派发共用同一派发决策；复核后若在实际派发前等待，须在取得派发资格时按该时刻重新复核。每个需要的保证必须有与本次参数的原 Producer 调用和物化值路径绑定的可信记录。逐条验证实际值、权威 Owner、Scope、该记录自身的 Correlation 和时间。描述符中的参数引用读取 Producer 派发前已物化、已校验并记录的 `arguments` 值。E.3 用 `query` 指 Observation 的实参，E.6 的 READ Operation 变体用 `arguments` 指 Operation 的实参。复核复用该值，不再求值 SourcePath。共享的目标维度必须一致，例如 Subject、PSI、Lifecycle 或 N4 实例；不同 Producer 的调用身份与事务按各自相关性校验。需要两条独立记录时，验证经 Owner 确认的来源记录身份或独立来源；同一底层记录的多个引用不能满足独立性。
3. Owner 的描述符规定该保证如何处理同一事实的多个记录。事实比较键由权威 Owner、该 Owner 内大小写敏感的非空 `fact` ID 和规范化 Scope 组成。`ue.registration` 是合法 ID；ID 的拼写或前缀本身不建立跨 Owner 等价关系。若命题只关于一次原调用，该调用身份必须是 Scope 的一部分。候选限于当前 Invocation 已接纳且由相应 Owner 验证、匹配该事实键的记录。当前参数使用的记录还必须符合本次调用的 Producer 关联。其他 Producer 记录只可用于判定更新或冲突，并须通过其自己的原调用关联校验。不同 Scope 的记录互不覆盖；不为选证据而触发外部查询。
   - `exact` 用于原调用结果或不可变事实。同一事实键下可信记录的规范化事实值不一致时，结论为 UNKNOWN。
   - `latest` 用于可变化状态。Owner 必须声明可验证的排序键，例如权威版本号或该 Owner 的 observedAt。可信排序键最大的记录决定当前值；并列且值不同、或不能确定顺序时，结论为 UNKNOWN。在复核既有判定时，已接纳的较新记录只用于使旧绑定失效。Predicate 始终消费显式绑定的 Producer 值；要使用新值必须显式绑定新 Producer。不得回退到旧记录绕过更新值已过期或不可用的情况。并列同值不构成冲突，但原绑定仍须位于最大排序键且有效。
   - 若多个保证要跨 Owner 比较同一事实，可信 Owner 契约必须显式声明共同事实身份、Scope 映射和可比较值。每个保证先在自身权威范围内按规则选出当前值。多个所需保证对同一事实给出不同的当前值时，该 Predicate 为 UNKNOWN。需要由一个权威来源先融合多个来源时，应由该 Owner 发布明确的融合结果和保证。不同事实之间的业务关系由 Predicate 显式判断。
4. Freshness 应给出时间基准和有效区间。使用 `maxAgeMs` 时，必须为正整数，并满足 `0 <= checkedAt - timestamp < maxAgeMs`。缺少时间基准、时间晚于本次校验时间或到达有效期上界均不可用。先按第 3 项确定当前版本，再检查该版本及原绑定的有效期。Invocation 已接纳的后来记录可以使早先通过的入口或 Goal 判定失效。
5. 只有全部要求成立才执行 evaluator 并接受其 PASS 或 FAIL；否则沿 UNKNOWN。Runtime 记录支撑实际判定的来源绑定及证据。入口派发与 SUCCEEDED 前按 §12.9 在新的校验时间和已接纳记录视图上复核同一原绑定；原绑定被取代时直接认定复核不通过，按 §12.8 停止并保留先前判定。即使后来记录有效且值相同，也不自动换绑、重新求值或重走旧 Predicate 的路由。

### 17.3 Predicate Script 的 Evidence 投影

业务参数按名称传递；`input.evidence` 为 Runtime 生成的只读保留命名空间，业务参数不得命名为 `evidence`。

~~~python
input = {
    "subscription": {"dnn": "internet", "status": "ACTIVE"},
    "requestedDnn": "internet",
    "evidence": {"subscription": {"refs": ["evidence-ref-1"]}},
}
~~~

`evidenceUsed` 仅报告 Script 实际引用的已附加记录，可为空；Runtime 独立记录满足各项保证的证据。Script 不得创建、重绑或扩大证据。Runtime 在 Script 返回后、选择路由前，将 `evidenceUsed` 与该次调用的全部 `input.evidence.<parameter>.refs` 的并集比较。报告的任一 Ref 不在并集中时，结果无效，沿 UNKNOWN。CEL 只读取声明的业务参数，接受同一套 Runtime Evidence 检查。

## 18. Fact、Observation、Evidence、State 的区别

| 名称 | 回答的问题 | 示例 |
|---|---|---|
| Fact | 要判断的业务命题是什么？ | UE 目标 Session 已建立 |
| Operation Result | 一次操作返回了什么？ | PCF Create 返回 association handle |
| Observation Query | 如何向权威 Owner 查询？ | 查询 SMF N4 资源状态 |
| Observation Result | Owner 返回什么事实？ | 当前 Session 对应 N4 pair |
| Evidence | 为什么相信这个值？ | Owner 记录、Invocation、Correlation、时间 |
| State | Host / Owner 保存什么状态？ | 生命周期、资源责任记录 |
| Host Context | Skill 被允许读取什么？ | 本次已校验的 Host Context |

State 不自动等于 Evidence；Handle 不自动等于 State；Mutation 成功不自动等于业务 Fact；Observation Result 不自动等于 PASS；Evidence Ref 不包含业务 Payload。

---

# 第六部分：执行语义、异常与恢复

## 19. Invocation 生命周期

1. Host 接收 Invocation；
2. Root Router 选择唯一 Skill；
3. Host 校验入口、授权和运行条件；
4. Host 物化本次 Invocation 的可信上下文，Runtime 按 §11.5 分别校验 Host Context 和调用方 Request；
5. Runtime 创建隔离 Invocation；
6. Procedure 从 start 指定的入口 Node 执行；Invocation 级入口门禁可以由显式 Observation 获取所需事实，再由 Precondition 作出判断；
7. 每个 Node 只执行其声明的一个主动作、显式 arguments 和 on 路由，不存在隐式的 Node 内部 Preconditions / Postconditions；
8. 必要时显式执行 Observation Query，Predicate 只消费已物化输入和 Host 附加 Evidence；
9. Mutation 结果不确定时按 §20 调和原调用或停止；
10. 到达 SUCCEEDED Terminal 时按 §12.9 检查实际路径的 Goal PASS 和责任状态；
11. Host 记录结果、Evidence、Trace 和资源责任。

必需步骤不得静默跳过。

## 20. READ、MUTATION 与 Reconcile

READ 必须校验 Capability、Effect、Input / Output Schema、Scope、Producer Invocation 和 Evidence。MUTATION 派发前还须校验入口门禁、Deadline、取消状态，并持久化原始调用身份、输入、Scope、Correlation 和结果责任。按 §12.8 处理准入失败或强制停止。

### 20.1 提交状态与输出

Runtime 只用可信且关联到本次原调用的证明记录提交状态。Owner 回包可同时包含提交证明和业务输出；二者按各自契约校验。以下规则也适用于超时、损坏回包、错误 Scope / Correlation 或未知 Outcome：

| 已派发 Mutation 的校验结果 | 路由或停止 |
|---|---|
| 提交证明有效，且 SUCCEEDED 边所承诺的输出及其保证均有效 | 记录已提交，沿 SUCCEEDED；无输出的 callable 按其已发布契约处理 |
| 提交证明有效，但 SUCCEEDED 边所承诺的输出缺失、无效或无法关联 | 保留已提交，隔离无效输出，记录 `COMMITTED_OUTPUT_UNAVAILABLE` 并按 §12.8 停止。该情况有已确认的外部变更待核实，发布 SAFE_STOPPED |
| Owner 明确证明原调用未提交 | 记录未提交。若可验证的 Owner 结果属于已声明的确定失败类别，且该类别由 Owner 保证没有遗留副作用，沿 FAILED。其余已证明未提交的情况沿 NOT_COMMITTED。FAILED 边不授予重试资格 |
| 没有可采信的提交或未提交证明，或可信证明之间存在未解决矛盾 | 保留原调用和迟到结果责任，沿 OUTCOME_UNKNOWN |

副作用保证由 Mutation Owner 在失败类别契约中声明。Runtime 验证结果确属该类别及本次原调用。可派发的 Mutation 契约必须声明 OUTCOME_UNKNOWN。NOT_COMMITTED 和 FAILED 由 Owner 契约按支持结果声明。出现未声明的已验证结果时，保留提交状态并按 §12.8 停止，禁止映射到成功。

来源不可信或关联错误的回包不能作为提交证明。独立有效的提交证明可以来自同一回包中独立验证的证明，也可来自 Owner 已交付且已验证的记录；本步骤不触发隐式查询。网络超时、未收到输出及 Schema 错误都不能证明未提交。

### 20.2 调和与受控新尝试

1. 有安全 Owner 契约时，Compiler 要求 OUTCOME_UNKNOWN 边直接进入对应 Reconcile。Runtime 校验本次授权、原调用身份、Scope、Correlation、预算、Deadline 和取消状态后，对同一次原调用至多派发一次。Reconcile 不引入新的业务副作用。
2. 没有安全契约时，OUTCOME_UNKNOWN 边必须直接指向 UNRESOLVED 或 SAFE_STOPPED。已有安全契约但当前不能派发时，Runtime 直接按 §12.8 停止。两种情况都保留原调用和责任。
3. Reconcile 确认 COMMITTED 或 NOT_COMMITTED 时，更新原调用状态。若 COMMITTED 契约承诺恢复输出，只有有效的 Reconcile 自身输出才随 COMMITTED 边提供；提交已确认但承诺恢复的输出无效时，按 §20.1 的 COMMITTED_OUTPUT_UNAVAILABLE 停止。契约未承诺输出时，后续节点可以显式读取权威状态。原 Mutation 丢失的输出不可用。COMMITTED 只更新原调用的提交状态。要到达 SUCCEEDED，该路径仍须通过新的 Goal Postcondition PASS（§12.9）。
4. Reconcile 缺少有效结论时沿 UNRESOLVED 边。该边必须直接进入停止 Terminal，Runtime 按 §12.8 选择实际终态。普通业务查询不能替代原调用调和。
5. 若另一个显式节点会重发同一业务 Mutation，只有它的每条到达路径都经过同一原调用的 NOT_COMMITTED 边（原 Mutation 或其 Reconcile）并持有 Owner 对该原调用的未提交证明，且 Owner 契约允许时，才可派发。该记录是 §20.1 第三行的 Owner 证明，可来自原调用或其 Reconcile，Runtime 保存并复核它与原调用的关联。仅有边名或 Runtime 自记的状态不足以授予重试资格。是否为同一业务尝试按 Owner 契约定义的调用与业务身份判定，不能只比较图节点 ID。Compiler 检查该路径条件，Runtime 复核证明、Scope 和 Owner 的重试约束。

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

READ Operation 与 Observation 的合法 Outcome 为 SUCCEEDED、FAILED、DENIED、UNKNOWN。Mutation 的合法 Outcome 为 SUCCEEDED、FAILED、DENIED、NOT_COMMITTED、OUTCOME_UNKNOWN。Reconcile 使用 §12.7 的结果，Procedure Script 使用 SUCCEEDED 或 FAILED。每个节点的路由键必须与其契约声明的 Outcome 集合完全一致。未能产生有效业务 Outcome 的 Runtime 异常按 §24.2 处理。未识别状态不得映射为 SUCCEEDED。

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

同一绑定点先校验参数数量、SourcePath 及其可用性，再校验类型和 Predicate Evidence 要求。若前一项失败，Compiler 不依据未经解析或不兼容的值推导后续错误。依赖、导出 Owner 或 Schema 无法解析时，先报告相应的链接错误。

| 错误 | 示例 | 要求 |
|---|---|---|
| YAML_PARSE_ERROR | 缩进、重复 Key、非法类型 | 阻止构建 |
| SOURCE_ROOT_INVALID | 文件根结构与文件角色不匹配 | 阻止构建 |
| LANGUAGE_TARGET_UNSUPPORTED | BuildRequest 指定的语言目标不受支持 | 阻止构建 |
| UNKNOWN_FIELD | 未定义语义字段 | 阻止构建 |
| DUPLICATE_ID | Procedure / Node / Predicate 重名 | 阻止构建 |
| PROCEDURE_START_MISSING | Procedure start 指向的入口节点不存在 | 阻止构建 |
| FINAL_POSTCONDITION_MISSING | 有可达 SUCCEEDED，但没有匹配 Contract Goal 的 Postcondition | 阻止构建 |
| FINAL_POSTCONDITION_GOAL_MISMATCH | Postcondition 的 goal 不等于 Contract Goal | 阻止构建 |
| ENTRY_PRECONDITION_BYPASSED | 可到达 Mutation 而未经过全部入口 PASS 边 | 阻止构建 |
| SUCCESS_BYPASSES_FINAL_POSTCONDITION | SUCCEEDED Terminal 可绕过最终 Postcondition PASS | 阻止构建 |
| CONTROL_FLOW_CYCLE | vNext DAG 中出现循环或 back-edge | 阻止构建 |
| SOURCE_PATH_INVALID | SourcePath 使用未支持的根、索引、动态表达式、未声明的 Schema 路径段，或 Node ID 使用保留的根名 | 阻止构建 |
| CONTROL_FLOW_DANGLING | 路由指向不存在 Node | 阻止构建 |
| CONTROL_FLOW_AMBIGUOUS | 多个主动作 | 阻止构建 |
| DEPENDENCY_REQUIREMENT_INVALID | dependencies 的值不是稳定 Package ID 字符串 | 阻止构建 |
| DEPENDENCY_ALIAS_MISSING | SourcePath / Schema 引用的 Alias 未在 Contract 声明 | 阻止构建 |
| DEPENDENCY_SNAPSHOT_MISSING | Contract 声明的实际使用依赖没有 Snapshot | 阻止构建 |
| DEPENDENCY_IDENTITY_UNVERIFIED | 缺少与别名、快照摘要绑定的可信身份元数据 | 阻止构建 |
| DEPENDENCY_ID_MISMATCH | Contract 与可信元数据声明的 Package ID 不同 | 阻止构建 |
| DEPENDENCY_OWNER_MISMATCH | 导出自带 Owner 与可信归属不一致，或 Owner 未获授权 | 阻止构建 |
| DEPENDENCY_EXPORT_OWNER_UNVERIFIED | 多 Owner 快照缺少某个导出的可信归属，或该归属重复、歧义 | 阻止构建 |
| DEPENDENCY_DUPLICATE | 同一 Alias 多份快照、或同一身份被歧义覆盖 | 阻止构建 |
| CONTEXT_SCHEMA_UNDECLARED | 读取 Host Context 字段但 Contract 未声明 contextSchema | 阻止构建 |
| CONTEXT_SCHEMA_MISMATCH | Context Schema、别名、字段路径或 Owner 不一致 | 阻止构建 |
| CONTEXT_REQUEST_COLLISION | Host Context Schema 声明或允许保留属性 request | 阻止构建 |
| REQUEST_SCHEMA_MISSING | 使用 context.request 但 Contract 未声明 Request Schema | 阻止构建 |
| ACTION_LIMIT_INVALID | limits.maxActions 不是正整数 | 阻止构建 |
| EXPORT_ID_MISSING | callable / Schema 不存在 | 阻止构建 |
| EXPORT_ID_AMBIGUOUS | 导出身份歧义 | 阻止构建 |
| SCHEMA_MISSING / INVALID | 缺失或非法 Schema | 阻止构建 |
| INPUT_REQUIRED_MISSING | 缺少必填输入 | 阻止构建 |
| INPUT_TYPE_MISMATCH | Source 不可赋给 Target | 阻止构建 |
| INPUT_NULLABILITY_MISMATCH | nullable Source 绑定非 nullable Target | 阻止构建 |
| SOURCE_NOT_AVAILABLE | Producer 非所有路径可用，例如 Reconcile COMMITTED 后引用丢失的原始成功输出 | 阻止构建 |
| RECONCILE_OUTPUT_UNAVAILABLE | Reconcile 后使用未由 Owner 声明可恢复的输出 | 阻止构建 |
| ROUTE_OUTCOME_MISSING / ROUTE_OUTCOME_UNKNOWN | 规范 Outcome 缺少路由，或路由键不属于精确契约 | 阻止构建 |
| PREDICATE_ARITY_MISMATCH | 参数数量不一致 | 阻止构建 |
| PREDICATE_TYPE_MISMATCH | 参数类型不兼容 | 阻止构建 |
| EVIDENCE_GUARANTEE_LINK_INVALID | `provides` 无法解析到唯一保证描述符，或 Producer、Outcome、值路径或实参引用不匹配 | 阻止构建 |
| PREDICATE_EVIDENCE_UNSATISFIABLE | 参数绑定无法提供所声明的 Evidence 保证或缺少可验证的关联约束 | 阻止构建 |
| RECONCILE_CONTRACT_INVALID | UNKNOWN 路由与安全 Reconcile 契约不匹配、无法绑定原调用或 UNRESOLVED 路由未直接停止 | 阻止构建 |
| CAPABILITY_NOT_GRANTED | 未授予 Capability | 阻止构建 |
| CAPABILITY_MAPPING_MISSING | callable 没有唯一 Capability | 阻止构建 |
| EFFECT_MISMATCH | Tool 与 Capability Effect 不一致 | 阻止构建 |
| SCRIPT_CONTRACT_INVALID | Script 入口 / TypedDict 不合规 | 阻止构建 |
| UNSUPPORTED_WAIT | 出现 Wait / Await | 阻止构建 |
| UNSUPPORTED_V02_SYNTAX | 使用旧版隐式语法 | 阻止构建 |

`UNREACHABLE_NODE` 是警告，定位从 `start` 不可达的节点。该警告本身不阻止构建，节点仍须通过语法和链接校验。

Compiler 不得为让文件编译而创建不存在的 Schema、用 object 逃逸、猜测 Operation ID、扩大 Capability、把 UNKNOWN 改成 PASS、静默删除未知字段或把旧语法映射成新语义。

### 24.2 Runtime 异常

回包无法解码时，记录 `RESPONSE_DECODE_FAILED`，再按调用类型处理。已派发 Mutation 在缺少独立有效提交证明时沿 OUTCOME_UNKNOWN；有独立提交证明时按 §20.1 处理，承诺的输出不可用时安全停止。
下表中的异常码用于诊断，与节点 Outcome 和 Invocation 终态分别记录。READ / Observation 回包无法支持该次查询结果时隔离输出，沿 Owner 契约的 UNKNOWN 边；没有该边时按关键事实不确定停止。纯 Procedure Script 输出无效沿 FAILED 边；缺少该边时按确定执行错误停止。若异常发生在新动作派发前，只有 `DENIED` 等由契约声明的派发前 Outcome 可沿图路由；门禁失效、全局限制和 Reconcile 无法派发直接按 §12.8 停止。全局取消、Deadline 和预算限制优先于继续沿图派发。

| 异常 | 处理原则 |
|---|---|
| AUTHORIZATION_DENIED | 不派发。普通调用有 DENIED 边时沿该边；Reconcile 或未声明 DENIED 时按 §12.8 停止 |
| EFFECT_MISMATCH | Fail-closed |
| TOOL_UNAVAILABLE | 派发前为确定执行错误；已派发且提交状态不可证实时按 §20；READ / Observation 结果未知时按本节规则 |
| INPUT_VALIDATION_FAILED | 拒绝调用 |
| RESPONSE_DECODE_FAILED | READ / Observation 沿 UNKNOWN 或按事实不确定停止；Mutation / Reconcile 按 §20 验证独立证明并决定结果 |
| OUTPUT_SCHEMA_INVALID | 已解码的输出未通过 Schema 校验。隔离输出；READ / Observation / Script 按本节失败规则处理，Mutation 按 §20.1 独立验证提交证明 |
| SCOPE_MISMATCH / CORRELATION_MISMATCH | 已派发 Mutation / Reconcile 按 §20；其他调用结果隔离，按本节失败规则处理。Predicate 所需证据不匹配时沿 UNKNOWN |
| EVIDENCE_MISSING / STALE / CONFLICT | Predicate 沿 UNKNOWN；入口或 Goal PASS 复核失败按 §12.8 停止；调用结果的强制保证无效时按 §20.1 或本节失败规则处理 |
| DEADLINE_EXCEEDED / CANCELLED | 不再派发任何 Procedure 动作。记录已派发调用的已知状态及迟到结果责任，按 §12.8 停止 |
| OUTCOME_UNKNOWN | 按 §20 调和原 Mutation 或停止并保留责任 |
| RECONCILE_UNRESOLVED | 沿 Reconcile 的 UNRESOLVED 边进入停止 Terminal，实际终态按 §12.8 |
| COMMITTED_OUTPUT_UNAVAILABLE | 保留已确认提交，隔离无效输出，按 §20.1 停止 |
| ENTRY_PRECONDITION_INVALIDATED / PRECONDITION_INVALIDATED | 入口或局部门禁复核失败，不派发受保护的 Mutation，按 §12.8 停止 |
| TERMINAL_STATE_MISMATCH | 按 §12.8 发布实际终态并记录声明值 |
| DUPLICATE_RESOURCE | 诊断保留其来源。Predicate 有充分证据证明命题不成立时沿 FAIL。已派发 Mutation 按 §20.1 分类，只有 Owner 证明未提交且该确定失败类别保证没有遗留副作用时才沿 FAILED。只有重复资源的诊断且提交状态无可信证明时沿 OUTCOME_UNKNOWN |
| STALE_LIFECYCLE | 按 §12.8 停止当前尝试 |
| PARTIAL_COMPLETION | 需要停止且有已知部分完成时发布 SAFE_STOPPED，持久化已知资源及责任 |
| OWNER_CONTRACT_UNAVAILABLE | 未派发时为确定执行错误；已派发 Mutation 的提交状态不可证实时按 §20 |
| ADMISSION_CONTEXT_INVALID | Host Context 必需字段缺失、Schema 校验失败或关联引用未通过 Host 准入校验时拒绝启动 |
| ACTION_BUDGET_EXCEEDED | 不启动下一次 Action；保留已发生的外部副作用及未决调用责任，按 §12.8 停止 |
| CONCURRENT_MODIFICATION | 校验 Scope 和版本；失败时不派发新动作，按 §12.8 停止 |

## 25. 典型业务异常

- **UE 尚未注册：** 必须通过可信 Host Context 或 Owner Observation 证明。请求中有 SUPI 不代表 UE 已注册。明确未注册按业务规则 FAIL；无法查询则 UNKNOWN。
- **UDM 无数据：** 明确无订阅数据可按业务规则 FAIL；UDM 不可用则 UNKNOWN；UE / DNN / S-NSSAI 不匹配则拒绝结果；不得用上一个 UE 缓存补齐。
- **UDM Subscribe 响应丢失：** 不得重新发送新 Subscribe。对原 Mutation 执行可用的 Owner Reconcile。确认已提交不等于原成功 Response 可用；只能使用 Reconcile 保证恢复的类型化结果，或再次独立 Observation 验证当前状态。确认未提交且业务契约允许才可发起受控新尝试；无法判断时按 §12.8 停止。
- **PCF Association 已存在：** Create 前验证准确的 Pre-N4 状态。已有冲突 Association 必须停止 Create。查询为空与查询失败不能混为一谈。
- **N4 尚未完成：** N4 异步建立属于 UPN.CREATE_UP_SESSION 内部完成责任。不得在最终完成前返回成功。结果必须关联本次 Policy Association、Lifecycle 和 Session Instance。Skill 不定义 Wait Loop。
- **AMF N1/N2 Transfer 部分失败：** 区分请求未发送、已发送但未知、明确失败和明确成功。传输超时不能解释为 AMF 未收到。保留 Operation Ref、目标 AMF、Response Artifact 和 Evidence。
- **RAN Setup 成功但 N4 Forwarding 失败：** 不得将 Session 标记成功。记录已完成资源和未完成资源，保留资源责任 Owner 和句柄，进入 SAFE_STOPPED。
- **多 Invocation 并发同一 UE：** 使用各自 Invocation / Lifecycle / PSI / Operation Ref。不能通过“最新记录”选择资源，不能把 A 的 Hold 用到 B 的 Mutation。
- **同一 UE 的两个 PSI：** PSI 必须参与 Session Scope。一个 PSI 的 N4 / Policy Association 不得绑定到另一个 PSI。
- **Observation 过期或冲突：** 过期结果不能证明当前状态；不同 Lifecycle 结果不能合并；多个 Owner 冲突时不能任意选择。无法消除冲突则 UNKNOWN。

---

# 第七部分：PDU Session 简化示例

## 26. 示例说明

本节展示语言结构，不重建全部 5GC ToolCatalog 或 36 个 Case。字段是教学示意，不构成 Owner Schema 发布声明。

流程：UE 注册验证 → UDM 查询 → UDM Subscription → PCF Association → N4 建立 → N1/N2 Transfer → RAN Setup → N4 Forwarding → 资源责任移交及最终验证。

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

UE 身份来自 Host Context，而不是调用方任意伪造的 UE Ref。

## 28. 5GC Skill 公共契约与 Procedure 入口

下表列出 Host Context 中实际开放的 5GC 字段。调用方请求另外通过 `context.request` 读取。

| SourcePath | 来源 |
|---|---|
| `context.ueRef` | Host 匹配运营侧 UE 档案后解析的引用 |
| `context.correlation.ingressRef` | Host 已接纳的 Fabric HELD 入口引用 |
| `context.correlation.lifecycleRef` | Host 独立解析并校验的生命周期绑定 |

~~~yaml
# assurance/contract.yaml（Owner ID 为教学占位，非已发布契约）
goal: pdu_session.initial_request_fulfilled
requestSchema: schemas/establishment-request.schema.yaml
contextSchema: ca-context::urn:connectionagent:ca:context:invocation:v1
dependencies:
  ca-context: urn:example:connectionagent:host-context
  ca: urn:example:connectionagent:5gc-tool-contracts
capabilities:
  - fivegc-session-read
  - fivegc-session-mutation
  - fivegc-session-assurance
  - fivegc-session-responsibility
~~~

~~~yaml
# assurance/procedure.yaml（只展示入口；完整简化流程见 §30）
start: observe-ue-registration
nodes:
  observe-ue-registration:
    observation: ca::ue.registration.current
    arguments:
      ueRef: context.ueRef
    'on':
      SUCCEEDED: check-ue-registration
      FAILED: failed
      UNKNOWN: unresolved
  check-ue-registration:
    precondition:
      entry: true
      predicate: createdsession.ue.registered
      arguments:
        - observe-ue-registration.output
    'on':
      PASS: read-udm-subscription
      FAIL: failed
      UNKNOWN: unresolved
  # 后续节点见 §30；此片段不能单独作为完整 Procedure 编译
~~~

这两个文件的职责不能合并：只有 Contract 可以声明 Goal、公共 Schema、依赖与 Capability Grants；只有 Procedure 承载执行图和最终 Postcondition。此处的 urn:example 身份是教学样例，不宣称真实 Owner 已发布或可以通过当前 Compiler 链接。完整可链接的目标样例需要 Owner 正式快照和 §34 的身份校验。

## 29. PredicateSet

~~~yaml
predicates:
  createdsession.ue.registered:
    parameters:
      - registration: ca::urn:connectionagent:5gc:observation:ue-registration:v1
    evidence:
      requires:
        registration: [ca::ue.registration-state]
    evaluator:
      type: cel
      expression: registration.state == "REGISTERED" &&
        registration.accessState == "ACTIVE"

  createdsession.udm.subscription_usable:
    parameters:
      - subscription: ca::urn:connectionagent:5gc:tool-output:udm-subscription-result:v1
      - requestedDnn: string
    evidence:
      requires:
        subscription: [ca::udm.subscription-state]
    evaluator:
      type: cel
      expression: subscription.dnn == requestedDnn &&
        subscription.status == "ACTIVE"

  createdsession.udm.session_profile_usable:
    parameters:
      - profile: ca::urn:example:ca:host-udm-session-profile:v1
      - requestedDnn: string
    evidence:
      requires:
        profile: [ca::udm.session-profile]
    evaluator:
      type: cel
      expression: profile.dnn == requestedDnn && profile.profileUsable

  # §30 中 create-pcf-association.output 与
  # inspect-pcf-after-reconcile.output 必须满足相同的 Owner 输出 Schema
  createdsession.pcf.association_owned:
    parameters:
      - association: ca::urn:connectionagent:5gc:pcf:association-result:v1
    evidence:
      requires:
        association: [ca::pcf.association-ownership]
    evaluator:
      type: cel
      expression: association.owned == true &&
        association.policyAssociationRef != ""

  createdsession.n4.initial_resources_ready:
    parameters:
      - initialResources: ca::urn:connectionagent:5gc:observation:createdsession.n4_initial_resources:v1
      - expectedBaselineRef: string
    evidence:
      requires:
        initialResources: [ca::smf.n4-resources]
    evaluator:
      type: cel
      expression: initialResources.bindingStatus == "CURRENT" &&
        initialResources.defaultFlowInstalled &&
        initialResources.uplinkEndpointBound &&
        initialResources.baselineEvidenceRef == expectedBaselineRef

  createdsession.session.network_ready:
    parameters:
      - ranSetup: ca::urn:connectionagent:5gc:observation:createdsession.ran_setup_result:v1
      - n4Forwarding: ca::urn:connectionagent:5gc:observation:createdsession.n4_forwarding_resources:v1
      - expectedSessionInstanceRef: string
    evidence:
      requires:
        ranSetup: [ca::ran.setup-state]
        n4Forwarding: [ca::upf.forwarding-state]
    evaluator:
      type: cel
      expression: ranSetup.result == "ACCEPTED" &&
        ranSetup.requiredFlowMatched &&
        ranSetup.smfPduState == "active" &&
        n4Forwarding.bindingStatus == "CURRENT" &&
        n4Forwarding.smfPduState == "active" &&
        n4Forwarding.requiredFlowMatched &&
        n4Forwarding.downlinkTunnelMatched &&
        n4Forwarding.gatesAllowForwarding &&
        ranSetup.currentSessionInstanceRef == expectedSessionInstanceRef &&
        n4Forwarding.currentSessionInstanceRef == expectedSessionInstanceRef &&
        ranSetup.requiredQfi == n4Forwarding.defaultQfi &&
        ranSetup.lifecycleRef == n4Forwarding.lifecycleRef

  createdsession.session.established:
    parameters:
      - ranSetup: ca::urn:connectionagent:5gc:observation:createdsession.ran_setup_result:v1
      - n4Forwarding: ca::urn:connectionagent:5gc:observation:createdsession.n4_forwarding_resources:v1
      - responsibility: ca-context::urn:connectionagent:5gc:observation:createdsession.resource_responsibility:v1
      - expectedSessionInstanceRef: string
    evidence:
      requires:
        ranSetup: [ca::ran.setup-state]
        n4Forwarding: [ca::upf.forwarding-state]
        responsibility: [ca-context::session.resource-responsibility]
    evaluator:
      type: cel
      expression: ranSetup.result == "ACCEPTED" &&
        ranSetup.requiredFlowMatched &&
        ranSetup.smfPduState == "active" &&
        n4Forwarding.bindingStatus == "CURRENT" &&
        n4Forwarding.smfPduState == "active" &&
        n4Forwarding.requiredFlowMatched &&
        n4Forwarding.downlinkTunnelMatched &&
        n4Forwarding.gatesAllowForwarding &&
        ranSetup.currentSessionInstanceRef == expectedSessionInstanceRef &&
        n4Forwarding.currentSessionInstanceRef == expectedSessionInstanceRef &&
        ranSetup.requiredQfi == n4Forwarding.defaultQfi &&
        ranSetup.lifecycleRef == n4Forwarding.lifecycleRef &&
        responsibility.lifecycleRef == ranSetup.lifecycleRef &&
        responsibility.managementState == "ACCEPTED" &&
        responsibility.allResourcesCovered &&
        responsibility.pendingResponsibilitiesRetained
~~~

本节的 5GC 类型引用用于说明绑定形状。完整示例依赖 Owner 发布相应 Schema、精确 callable 输出绑定和保证；可脱离外部仓库复核的完整链接输入见附录 E。UDM Get 的 `output.result` 表示本次 SM 数据读取；订阅 Create 的 `output.subscription` 与 Reconcile 后查询的 `output.subscription` 表示订阅资源状态。两种命题分别使用 Session Profile 和 Subscription Predicate。Session Profile 的 `urn:example` 结构用于教学，真实迁移以 Host 规范化 Get 输出为准。

## 30. Procedure

~~~yaml
# assurance/procedure.yaml — 公共声明仅在 §28 contract.yaml 中
start: observe-ue-registration
nodes:
  observe-ue-registration:
    observation: ca::ue.registration.current
    arguments:
      ueRef: context.ueRef
    'on':
      SUCCEEDED: check-ue-registration
      FAILED: failed
      UNKNOWN: unresolved

  check-ue-registration:
    precondition:
      entry: true
      predicate: createdsession.ue.registered
      arguments:
        - observe-ue-registration.output
    'on':
      PASS: read-udm-subscription
      FAIL: failed
      UNKNOWN: unresolved

  read-udm-subscription:
    operation: ca::sbi.udm.sm_data.get
    arguments:
      ueRef: context.ueRef
      dnn: context.request.dnn
      sNssai: context.request.sNssai
    'on':
      SUCCEEDED: check-udm-subscription
      FAILED: failed
      DENIED: failed
      UNKNOWN: unresolved

  check-udm-subscription:
    postcondition:
      predicate: createdsession.udm.session_profile_usable
      arguments:
        - read-udm-subscription.output.result
        - context.request.dnn
    'on':
      PASS: create-udm-subscription
      FAIL: failed
      UNKNOWN: unresolved

  create-udm-subscription:
    operation: ca::sbi.udm.sdm_subscription.create
    arguments:
      ueRef: context.ueRef
      sessionProfile: read-udm-subscription.output.result
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
    operation: ca::sbi.pcf.sm_policy.create
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
      dnn: context.request.dnn
      sNssai: context.request.sNssai
    'on':
      SUCCEEDED: verify-pcf-association
      NOT_COMMITTED: safe-stopped
      OUTCOME_UNKNOWN: reconcile-pcf-association
      DENIED: safe-stopped
      FAILED: safe-stopped

  verify-pcf-association:
    postcondition:
      predicate: createdsession.pcf.association_owned
      arguments:
        - create-pcf-association.output
    'on':
      PASS: create-n4-session
      FAIL: safe-stopped
      UNKNOWN: safe-stopped

  reconcile-pcf-association:
    operation:
      reconcile: create-pcf-association
    'on':
      COMMITTED: inspect-pcf-after-reconcile
      NOT_COMMITTED: safe-stopped
      UNRESOLVED: safe-stopped

  # Reconcile 已确认提交，但原 Create 成功响应不一定存在
  inspect-pcf-after-reconcile:
    observation: ca::pcf.policy_association.current
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
      policyAssociationRef: reconcile-pcf-association.output.policyAssociationRef
    'on':
      SUCCEEDED: verify-reconciled-pcf
      FAILED: safe-stopped
      UNKNOWN: safe-stopped

  verify-reconciled-pcf:
    postcondition:
      predicate: createdsession.pcf.association_owned
      arguments:
        - inspect-pcf-after-reconcile.output
    'on':
      PASS: create-n4-session
      FAIL: safe-stopped
      UNKNOWN: safe-stopped

  create-n4-session:
    operation: ca::UPN.CREATE_UP_SESSION
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
    'on':
      SUCCEEDED: transfer-n1n2
      OUTCOME_UNKNOWN: safe-stopped
      FAILED: safe-stopped
      DENIED: safe-stopped

  transfer-n1n2:
    operation: ca::sbi.amf.n1n2.transfer
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
    'on':
      SUCCEEDED: signal-ran
      OUTCOME_UNKNOWN: reconcile-n1n2-transfer
      NOT_COMMITTED: safe-stopped
      FAILED: safe-stopped
      DENIED: safe-stopped

  reconcile-n1n2-transfer:
    operation:
      reconcile: transfer-n1n2
    'on':
      COMMITTED: signal-ran
      NOT_COMMITTED: safe-stopped
      UNRESOLVED: safe-stopped

  signal-ran:
    operation: ca::SSM.SIGNAL_UE_AN
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
    'on':
      SUCCEEDED: modify-n4-forwarding
      OUTCOME_UNKNOWN: safe-stopped
      FAILED: safe-stopped
      DENIED: safe-stopped

  modify-n4-forwarding:
    operation: ca::UPN.MODIFY_UP_SESSION
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
    'on':
      SUCCEEDED: read-ran-setup
      OUTCOME_UNKNOWN: safe-stopped
      FAILED: safe-stopped
      DENIED: safe-stopped

  # 分开读取 RAN 与 UPF 权威结果，复用同一个已确认的 N4 实例。
  read-ran-setup:
    observation: ca::ran.setup.current
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
      sessionInstanceRef: create-n4-session.output.sessionInstanceRef
    'on':
      SUCCEEDED: read-n4-forwarding
      FAILED: safe-stopped
      UNKNOWN: safe-stopped

  read-n4-forwarding:
    observation: ca::n4.forwarding.current
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
      sessionInstanceRef: create-n4-session.output.sessionInstanceRef
    'on':
      SUCCEEDED: verify-network-state
      FAILED: safe-stopped
      UNKNOWN: safe-stopped

  verify-network-state:
    postcondition:
      predicate: createdsession.session.network_ready
      arguments:
        - read-ran-setup.output
        - read-n4-forwarding.output
        - create-n4-session.output.sessionInstanceRef
    'on':
      PASS: transfer-resource-responsibility
      FAIL: safe-stopped
      UNKNOWN: safe-stopped

  transfer-resource-responsibility:
    operation: ca-context::ca.session.resource_responsibility.transfer
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
      lifecycleRef: context.correlation.lifecycleRef
      sessionInstanceRef: create-n4-session.output.sessionInstanceRef
    'on':
      SUCCEEDED: read-resource-responsibility
      OUTCOME_UNKNOWN: reconcile-resource-responsibility
      NOT_COMMITTED: safe-stopped
      DENIED: safe-stopped
      FAILED: safe-stopped

  reconcile-resource-responsibility:
    operation:
      reconcile: transfer-resource-responsibility
    'on':
      COMMITTED: read-resource-responsibility
      NOT_COMMITTED: safe-stopped
      UNRESOLVED: safe-stopped

  read-resource-responsibility:
    observation: ca-context::ca.session.resource_responsibility.current
    arguments:
      ueRef: context.ueRef
      pduSessionId: context.request.pduSessionId
      lifecycleRef: context.correlation.lifecycleRef
    'on':
      SUCCEEDED: verify-final-state
      FAILED: safe-stopped
      UNKNOWN: safe-stopped

  verify-final-state:
    postcondition:
      goal: pdu_session.initial_request_fulfilled
      predicate: createdsession.session.established
      arguments:
        - read-ran-setup.output
        - read-n4-forwarding.output
        - read-resource-responsibility.output
        - create-n4-session.output.sessionInstanceRef
    'on':
      PASS: complete
      FAIL: safe-stopped
      UNKNOWN: safe-stopped

  complete:
    terminal: SUCCEEDED
  failed:
    terminal: FAILED
  unresolved:
    terminal: UNRESOLVED
  safe-stopped:
    terminal: SAFE_STOPPED
~~~

- 本图是完整的教学控制流。真实 Tool、Host journal 和 Capability 身份须由 Owner 发布。它简化了 Hold、Lifecycle Gate、N4 基线、资源句柄和部分 Reconcile，不可替代真实 5GC Skill 或改变既有流程。N4、RAN 与 Forwarding 的直达 UNKNOWN 停止边以该教学调用没有安全 Reconcile 契约为前提。AMF 的 COMMITTED 路径只表示 Owner 已确认原调用提交；随后仍须验证 RAN 和转发。
- 本例假设 PCF Reconcile 在 COMMITTED 上明确保证恢复精确 `policyAssociationRef`，并假设 UDM 的 SUCCEEDED / COMMITTED 在继续执行前已证明并登记本次确切订阅的资源责任。Owner 无法提供这些保证时应增加独立的权威验证或安全停止。
- 本例在 Host 已登记资源/迟到结果责任的前提下移交管理责任。派发移交前，Owner 必须验证所移交的确切资源及当前生命周期；图中省略了教学调用的内部句柄字段。网络状态先通过局部验收再移交。移交后从 Host journal 取得权威结果，最终 Postcondition 复用仍有效的 RAN 和 N4 值，并验证责任。教学移交只变更 Host 管理责任；若实际操作也会改变网络状态，必须提供移交后的权威证明。RAN、N4 和责任 Evidence 必须同时满足 §17。
- 例如 RAN 已完成、`modify-n4-forwarding` 返回 FAILED 或 OUTCOME_UNKNOWN 时，进入 SAFE_STOPPED。Host 保留 UDM 订阅、PCF Association、N4 实例及 RAN 的已知资源句柄、未决调用和原责任方，记录停止原因。不能直接重发 Forwarding 或把资源从责任记录中移除。
- 可复用满足同一保证、类型和有效期要求的既有 Operation Result，省去相应的 Observation。RAN、N4 和责任读取仍保持各自权威与准确业务关联。

## 31. Operation 与 Observation 对照

~~~yaml
# Operation：执行一个业务动作
create-policy:
  operation: ca::sbi.pcf.sm_policy.create
  arguments:
    ueRef: context.ueRef
    pduSessionId: context.request.pduSessionId

# Observation：只有在需要补充权威事实时才查询
read-policy-state:
  observation: ca::pcf.policy_association.current
  arguments:
    ueRef: context.ueRef
    pduSessionId: context.request.pduSessionId

# Postcondition：如果 Operation Result 已经充分，也可以不创建 Observation 节点
verify-policy:
  postcondition:
    predicate: createdsession.pcf.association_owned
    arguments:
      - create-policy.output
~~~

Operation 与 Observation 共用 ToolCatalog、Capability 和 Runtime Admission，但业务语义不同。Observation 是可选的事实获取机制，不是 Operation 的固定后继。Operation Result 可以直接作为 Predicate 输入；若需要独立权威查询，则 Observation 可以使用 Operation Result 中的资源引用和关联身份作为 arguments。

## 32. Python Script

Skill 自有 Python Script 有两种用途，但都不是 Tool、Capability 或自由执行环境：

1. **Procedure Script：** 承载确定性的本地数据计算、选择、转换和结构化结果生成。它通过 Operation 节点调用，不增加第五种 Procedure 节点。
2. **Predicate Script：** 承载 CEL 不适合表达的纯判断逻辑，由 Predicate 的 evaluator 引用。

### 32.1 Procedure Script

~~~yaml
prepare-policy-inputs:
  operation:
    script: scripts/build_pcf_policy_inputs.py
  arguments:
    subscriptionData: select-establishment-configuration.output.subscriptionData
    subscriptionSource: select-establishment-configuration.output.subscriptionSource
  'on':
    SUCCEEDED: create-policy
    FAILED: failed
~~~

- 唯一入口为 main(input: dict)。
- arguments 是该调用点的完整输入投影；Compiler 根据 Source Schema 推导只读输入类型环境，不要求作者另写 Script Input Schema。
- Script 必须返回严格 TypedDict。Compiler 从返回类型生成 Output Schema。`Literal` 声明允许值，受支持的 `Annotated` 元数据提供 Schema 约束，`NotRequired` 声明属性可缺失。输出路径是否可以直接绑定按 §13.3 校验。支持的类型与注解集合由 Script Contract 定义。
- 输出通过 node.output 暴露给后续 Producer / Consumer。
- Procedure Script 是纯本地 Operation：不得访问网络、HTTP、MCP、Shell、数据库、文件系统、凭据、环境变量、时钟或随机源；不得执行外部副作用。
- Procedure Script 不属于 ToolCatalog callable，不需要 Capability Grant，也不得声明 READ / MUTATION Effect。Host 仍负责沙箱、资源预算、超时和异常治理。
- Script 抛出异常、返回结构不符合 TypedDict 或输出 Schema 校验失败时，不得作为成功输出供后续节点消费。

### 32.2 Predicate Script

Predicate Script 的业务输入签名唯一来源是所属 Predicate.parameters；所有调用点的 arguments 必须按顺序、类型兼容地绑定这些参数。

~~~python
from typing import Annotated, Literal, TypedDict

class PredicateEvaluationResult(TypedDict):
    result: Literal["PASS", "FAIL", "UNKNOWN"]
    reasonCode: Annotated[str, {"minLength": 1}]
    evidenceUsed: list[str]

def main(input: dict) -> PredicateEvaluationResult:
    # input 中只有声明的业务参数和 Host 附加的只读 Evidence projection
    ...
~~~

- result 是驱动 Procedure PASS / FAIL / UNKNOWN 路由的唯一业务结果。
- reasonCode 是可诊断原因，不得改变三态语义。
- `evidenceUsed` 的路由前校验见 §17.3。Runtime 按 §17.2 独立检查并记录证据保证。
- Predicate Script 的 Output Schema 从严格返回 TypedDict 生成；不得再手工维护竞争性的 Output Schema。
- CEL Predicate 也遵循相同的三态语义；Runtime 负责将其规范化为统一 Predicate Evaluation Result，并保留本次输入与 Evidence lineage。
- Compiler / LSP 必须提供由 Predicate.parameters 派生的只读类型环境；不得执行 Python 函数体来猜测类型或行为。

### 32.3 通用安全边界

所有 Script 都必须确定性、可审查、可静态检查。不得动态导入、反射执行任意代码、访问外部系统或读取非显式输入。Script 只能实现 Skill 内部纯计算；数据获取必须由显式 Operation / Observation 完成，流程分支必须由 Procedure 的 Predicate 结果路由完成。
## 33. Cases

Case 是场景声明，不是执行图。可以记录场景输入、预期业务语义、路由、资源不变量、失败 / UNKNOWN 条件。Case 不得自行授予 Capability、定义 Tool Schema、代替 Owner Evidence 或声称已执行通过。

## 34. Dependencies 与 BuildRequest

Skill 源码只引用本包拥有的文件，或通过 Contract 声明的 Alias 访问 Owner 发布的精确 Schema / Callable 身份。不得携带 Git URL、分支、下载地址、依赖版本锁、digest、注册表地址或依赖获取指令。

### 34.0 最小依赖身份与链接规则

`contract.yaml` 的 `dependencies` 将每个别名直接映射到一个稳定 Package ID 字符串。版本、下载位置和快照内容不写进 Skill 源码。

~~~yaml
dependencies:
  ca-context: urn:example:connectionagent:host-context
  ca: urn:example:connectionagent:5gc-tool-contracts
~~~

复用 Compiler v0.1 已有的逻辑快照形状 `{dependencyId, digest, files}`。其中 `dependencyId` 是 Workspace 别名，`digest` 由 Compiler 从规范化文件集重算，二者均不能证明 Package ID 或 Owner。可信调用方依据既有来源配置、锁定快照和已验证 Owner 元数据，为同一 `(dependencyId, digest)` 提供稳定 Package ID 与允许的 Owner 身份。来源绑定可由 Studio 依赖目录或部署配置提供；上传内容或 MCP discovery 自报身份本身不构成可信绑定。

1. 对每个被引用的 Alias 链接唯一快照，并校验规范化路径、文件集及摘要。按同一 Alias 和实测摘要获取可信身份绑定，与 `Contract.dependencies[alias]` 精确比较。无可信绑定、同一 Alias 对应多个快照或身份不匹配均阻断构建。
2. 在该快照内解析唯一精确的 `alias::exportId`。用可信绑定核对导出 Owner，再校验 callable kind、Effect、Schema `$id`、引用闭包和 Evidence 保证。单 Owner 快照可由可信绑定为没有 Owner 字段的导出赋予该 Owner。多 Owner 快照必须由可信调用方提供显式的 `(exportKind, exportId) → owner` 归属；Owner 须在绑定的授权集合内。导出自带 Owner 字段时必须与可信归属一致。该规则也适用于引用闭包中实际链接的 Schema、Evidence 保证等导出。先解析唯一可信归属。多 Owner 快照中归属缺失、重复或歧义时报 `DEPENDENCY_EXPORT_OWNER_UNVERIFIED`。已有唯一归属，但 Owner 不在授权集合内，或与导出自带 Owner 不一致时，报 `DEPENDENCY_OWNER_MISMATCH`。Compiler 不按文件路径、`$id` 前缀或文件顺序猜测。
3. 外部 callable 还须在独立可信 CapabilityContracts 中，以精确 Owner、callable ID 和 kind 找到唯一归属的 Capability，再检查 Effect 与 Skill Grant。单纯链接成功不授予执行权。
4. 合法但未使用的 Contract 依赖产生 Warning。构建输入里的额外快照不得自动进入 Skill 链接范围。

`dependency.yaml` 不作为必需输入。此规则复用快照线协议及锁定信息；CA-SL 只要求可验证的身份关联。Studio / Compiler 仍须确认怎样传入这份可信绑定，以及如何传递多 Owner 快照的导出级归属；当前 v0.1 的 SHA-256 输入摘要按 Compiler 的路径与原始文件字节 framing 契约计算；CA-SL 复用该规则，YAML 重排、换行变化或 JSON 重编码均不能在摘要计算前替换原始字节。若调用方无法提供可信身份，保留链接错误。Compiler 只消费调用方提供的字节和可信元数据，语言版本与传输字段由 Compiler BuildRequest 版本管理。

摘要细节见 [Compiler v0.1 快照摘要](https://github.com/odango-chan/ca-skill-compiler/blob/b60024497b4865f705fa40e1b04bcc84032778d8/docs/design/dependency-snapshot-digest-v0.1.md)。参见 [Compiler PR #4 的 BuildRequest v0.1 契约](https://github.com/odango-chan/ca-skill-compiler/pull/4) 和 [Studio PR #150 的配置与快照设计](https://github.com/odango-chan/ca-skill-studio-demo/pull/150)。

### 34.1 Schema 的源格式与编译格式

Schema 的语义标准是受支持子集的 JSON Schema；JSON 与 YAML 只是同一数据模型的两种序列化形式。

- Skill 自有 Request Schema 的作者源码可以使用 YAML（例如 schemas/establishment-request.schema.yaml），并继续作为唯一可编辑源。
- Compiler 解析后必须先归一化到同一 Schema Model，再进行引用解析、组合、类型检查和生成。
- BuildResult 的 Schema 文件究竟输出 YAML 还是 canonical JSON，属于 Compiler Artifact Contract，不是 CA-SL 节点语法。建议机器消费的生成 Schema 使用 canonical JSON，以便稳定序列化和比较；但本 PR 不冻结该输出格式。
- 生成文件不得反向覆盖作者 YAML 源码。

### 34.2 外部 DependencySnapshot 与 Schema 闭包

- DependencySnapshot 是调用方为本次 Build 提供的不可变输入；Compiler 只解析实际引用的精确导出身份和 Schema $id。
- 不把整个外部 lib / DependencySnapshot 无差别复制到 Skill 或 Build Artifact。
- 若下游 Runtime / 部署包要求自包含，打包层最多收集本次构建实际可达的 Tool、Observation、Context、Capability 和 Schema 依赖闭包，并保留 Owner 身份、版本和来源；不得把未引用资源一并打包。
- 若 Runtime 支持按已锁定依赖身份解析，也可以在 Artifact 中保留精确外部引用，不嵌入所有依赖内容。
- “嵌入可达闭包还是保留外部引用”以及具体文件序列化格式属于独立的 Compiler / Deployment Artifact 设计，不阻塞本轮 CA-SL 语法评审。

Compiler MUST NOT 联网获取依赖、管理版本 / Lock / Cache / Workspace、执行 Python、执行 Tool 或声称 Runtime READY。
## 35. Skill Studio 与 LSP

Skill Studio 是 CA-SL 作者工作环境，不是第二个语言实现。应提供：

1. YAML 语法、缩进、字段补全和非法字段提示；
2. Skill 创建向导：选择模板 / 空白 Skill、定义 Goal、创建或选择公共 Request Schema；
3. Dependencies 视图：从可用公共目录选择 Host Context、ToolCatalog、Observation 和共享 Schema 契约；显示 Owner、稳定身份、导出内容和依赖影响；
4. Capabilities 视图：从可信部署 CapabilityContracts 选择授权范围，解释每个 Capability 包含的精确 callable 与 Effect；不得把依赖选择误当成授权；
5. Invocation Context 视图：选择 Host Owner 发布的 Context Schema，并将精确 Schema 身份写入 Contract 的 `contextSchema`；
6. Contract 编辑器：将 Goal、Request、Context、Dependencies 和 Capability Grants 持久化到 `assurance/contract.yaml`；
7. Dependency Resolution：获取作者选择的确切依赖快照并将其作为 BuildRequest 输入；版本 / 快照状态保存在 Studio 项目配置或 Build 输入，不写入 Skill 公共 Contract；
8. Skill / Procedure / Node / Operation / Observation / Capability / Predicate / Schema / Script 语义高亮；
9. Definition：跳转 ToolCatalog、Owner Schema 和 Python Script；
10. References：查询调用点；
11. Hover：Owner、Effect、Schema、Capability、Scope / Freshness / Evidence 保证；
12. Completion：只补全当前已选依赖快照中真实存在的导出身份；
13. Diagnostics：区分语法、链接、类型、授权和业务警告；
14. Procedure Designer：显示真实执行图、入口门禁、最终 Goal 标记及所有 PASS 覆盖分支。编辑最终 Postcondition 时从 Contract 提取 Goal 供选择；
15. Data Flow：展示 Context / Operation / Observation 到 Predicate 的值流、所需 Evidence 保证及其 Producer；
16. Package View：区分 Skill 自有文件、只读依赖和生成 Artifact；
17. Case View：展示语义义务，不伪装成 Runtime 结果；
18. Owner Inspection：展示 Schema / Tool / Observation 的 Owner 和导出身份。

依赖和 Capability 选择不是一次性的创建向导行为；作者后续可以在 Dependencies / Capabilities 视图增删声明、检查影响并重新解析。Studio 不得静默改变 Skill 的公共依赖或 Capability Grants。

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
5. Host 与各 Owner 确认 Evidence 保证导出、权威绑定、有效性规则和 Runtime 校验；
6. Schema ID 和 Dependency Alias 引用规则定稿；
7. Predicate.parameters、CEL / Predicate Script 与 Procedure Script 类型环境定稿，确认 Script Contract 支持的类型与注解子集（包括 `Literal`、`Annotated`、`NotRequired`）；
8. Procedure 四种节点、入口 / 最终门禁、DAG、SourcePath 和路由正负例；
9. 三个 5GC 异步完成 Operation 的 Owner 契约确认；
10. Studio / Compiler 确认可信快照身份绑定的来源、传输方式及多 Owner 归属，通过 Appendix E 链接正负例；
11. 完整 5GC PDU Skill 迁移演练；
12. Compiler 正负例与诊断验收；
13. Skill Studio 语义体验验收；
14. Native / WASM / Studio 语义一致性验证；
15. 独立确定 Compiler Artifact 的 Schema 序列化与外部依赖闭包策略。

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

请求可能已经在远端提交，只是响应丢失。直接发第二次可能重复创建资源或副作用。具备安全 Owner 契约和运行条件时，先调和原 Operation；其余情况按 §20 停止并保留责任。

## 54. 为什么区分 Capability 和 Operation？

Operation 是“能调用什么”；Capability 是“部署允许这一组什么能力”。Skill 可以声明需要某个 Capability，但不能自行把 Operation 加入其中或改变 Effect。

## 55. 为什么 Skill 不直接引用 Tool Adapter？

Adapter 是 Tool Owner 的实现细节。Skill 应引用稳定契约身份，而不是 HTTP URL、Python 类名或网元内部路径。

## 56. 为什么 Schema 不全部放在 Skill 的 schemas/？

因为这会产生影子契约。UDM、SMF、PCF、Host、Fabric 各自拥有不同业务数据和状态。Skill 复制 Schema 会导致 Owner 更新而 Skill 未同步，产生两套矛盾事实。

## 57. 为什么 Script 入口是 input: dict？

`dict` 是统一的 Python 调用容器。Procedure Script 的字典由节点 `arguments` 派生；Predicate Script 的业务字段由 `parameters` 与调用绑定确定，Host 可附加只读 Evidence refs。Compiler / LSP 应提供派生类型环境，不让作者维护重复 Schema。

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

## 67. 为什么不增加通用 computation Node？

判断与数据计算是两种不同的确定性职责。Predicate 定义纯判断，使用 CEL 或 Predicate Script 实现，并由 Precondition / Postcondition 节点调用。Procedure Script 则负责本地数据选择、转换和结构化结果生成，通过 Operation 节点的 script 目标执行。两者都不需要增加通用 computation 节点，也不能把数据转换伪装成 PASS / FAIL / UNKNOWN 判断。

## 68. 为什么 Operation 和 Observation 使用具名 arguments，而 Predicate 使用位置 arguments？

Operation / Observation 的输入由 Owner 发布的 JSON Schema 定义，字段名是接口契约的一部分，因此使用具名映射。Predicate 声明有序参数签名，调用时按签名位置传入，因此使用列表。两者都省略 from/value 包装，但静态类型和来源检查不变。

## 69. Operation Result 足够时为什么不执行 Observation？

Observation 是可选的事实获取机制。若 Operation Result 已包含目标 Predicate 所需的业务事实、Scope、Correlation、Freshness 和 Evidence，额外查询只会增加延迟和失败面。只有信息不足或业务明确要求独立权威观察时，才执行 Observation。

## 70. Operation Result 能否作为 Observation 的输入？

可以。Operation Result 可以提供 Observation Query 所需的资源引用、Session Instance、SEID 或 Correlation。但 Observation Result 必须由 Observation Owner 实际查询产生，不能把 Operation Result 包装成 Observation Result，也不能丢失其原始 Producer 身份。

## 71. 为什么 Reconcile 不是独立节点类型？

Reconcile 是原始 Mutation Operation 的受约束调和模式。把它表达为 operation.reconcile: <original-node>，可以复用 Operation 的授权、Owner 契约和 Runtime Admission，同时明确只能调和原始 Mutation，不能发起新的业务 Mutation。

## 72. 为什么 Contract 仍需要 dependencies？

Skill Studio 和 Compiler 需要知道作者实际依赖哪些公共 Owner 契约；不能仅从 Procedure 中偶然出现的 callable 反向推断全部 Context / Schema 要求。Contract 声明稳定 Package 身份，构建调用方提供具体快照和可信身份绑定；依赖可链接不意味着已经获得 Capability 授权。

## 73. 为什么不在 Contract 中写具体版本和下载地址？

这是作者希望使用哪个公共契约，与工作空间当前解析出哪份字节的分离。Contract 固定稳定 Package / Owner 语义，Studio 或 Build 调用方提供确切快照。Schema 本身的精确 $id 若含不可变版本分量必须保留；不等于在 YAML 根重复 apiVersion。

## 74. Reconcile 确认 COMMITTED 后为什么还需要检查输出？

COMMITTED 确认原调用的提交状态。Owner 明确承诺恢复输出且输出通过校验时，后续可以消费 Reconcile 自身的 Schema 所描述的输出，例如只恢复资源 Ref。承诺恢复但输出无效时按 §20.2 停止。契约未承诺输出时，可显式执行权威 Observation；原调用丢失的输出始终不可用。

## 75. Invocation Context 与入口 Observation 各提供什么？

Invocation Context 提供 Host 在准入时已经确认的 UE 和入口、生命周期关联引用。入口 Observation 在 Procedure 开始后读取权威 Owner 掌握的实时状态，例如 UE 注册或 N4 资源。

## 76. 为什么 Reconcile COMMITTED 后还需要新的 Goal PASS？

COMMITTED 只确认原 Mutation 已提交，可按 Owner 契约恢复该调用的部分输出。此前的 Goal PASS 不能覆盖后续 Mutation 的影响。§30 的 UDM Reconcile 提交分支继续到 PCF，最终仍执行 Goal Postcondition；直接从 COMMITTED 走到 SUCCEEDED 会被 Compiler 拒绝。`COMMITTED → READ SUCCEEDED → 新的 Goal PASS → SUCCEEDED` 可以通过证明覆盖校验。若该分支进入停止终态，则按 §12.8 判断，无需 Goal PASS。

## 77. 为什么复核不会自动用新 Evidence 重算旧 Predicate？

Predicate 的业务值和 Evidence 共同绑定到一次具体调用。较新的已接纳记录可使旧判断失效；派发或结束检查据此停止，保留先前 PASS 的执行记录。若业务允许用新状态继续，Procedure 需要显式绑定新的 Producer 并执行新判断。自动换绑会改变原路径的业务判断和审计记录。

## 78. 为什么可选输出字段不能直接作为 SourcePath？

可选字段在成功响应中也可能缺失。当前图没有能证明字段存在的类型收窄规则，也不自动补默认值。调用方可以绑定必定存在的外层对象，由消费者处理可选字段；若业务要求直接绑定该字段，Owner 须通过精确输出 Schema 保证它存在。

## 79. 为什么 CA-SL 不重写快照摘要算法？

Compiler 的 BuildRequest 契约定义原始文件字节的 SHA-256 framing，Studio 和 Compiler 使用同一规则。CA-SL 负责把实测摘要和别名关联到可信 Package ID、Owner 与精确导出。重复定义摘要算法会让同一份快照在两套规则下产生不同身份。

## 80. 为什么附录 E 的负例采用基线与最小变更？

E.1–E.4 给出独立链接基线。E.6 从 E.1–E.4 的成功输入派生链接与绑定负例。E.7 从 §12.1 的行为图派生控制流负例，并从 E.4 派生证据复核负例。部分 Mutation、跨路径和多次取证用例仍需实际 Owner 测试输入；E.5 保留这些验收要求，执行夹具由相应实现交付。

## 81. 为什么现在还不能冻结各层契约？

本稿用自包含示例表达语言规则。正式冻结还需要同一组用例在 Compiler、Studio 和 Runtime 中得出一致结果。ToolCatalog、CapabilityContracts、Evidence 描述符的线格式以及异步 Operation 的行为保证由各 Owner 确认，验收项见 §45。

## 82. 为什么允许 start 直接指向 Goal Postcondition？

`start` 标识首个执行节点，入口门禁由独立的 Precondition 节点表达。只判断已准入 Context 的 Skill 可以从 Goal Postcondition 开始。它进入时没有证明，只有自身的 PASS 出边才能建立证明。若需要入口门禁与最终判断，应使用两个节点；强制插入无业务作用的起始节点会增加路径，却不会增加证明。

## 83. 为什么未声明的输出字段报 SOURCE_PATH_INVALID？

Compiler 已找到对应的导出和 Schema，接下来要验证该 Schema 内的路径。字段未声明时路径本身无效。若字段已声明但当前分支没有产生该输出，才报告 SOURCE_NOT_AVAILABLE。EXPORT_ID_MISSING 和 SCHEMA_MISSING 用于导出或 Schema 自身缺失。

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
| D-12 | Mutation UNKNOWN 按 §20 调和或停止 | 保留原调用和资源责任 |
| D-13 | Script 仅实现确定性本地计算 | Procedure Script 是 Operation 节点的纯本地目标；Predicate Script 是 Predicate evaluator；均不调用外部系统 |
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
| D-24 | 保留作者维护的 contract.yaml | 公共 Goal、Request、Context、Dependencies 和 Capability Grants 不由 Compiler 猜测 |
| D-25 | Contract 与 Procedure 分离 | Procedure 只声明执行图与最终 Postcondition，禁止重复根字段 |
| D-26 | 快照身份与 Owner 校验 | 可信调用方将 Package ID / Owner 绑定到别名及实测摘要；Compiler 校验链接 |
| D-27 | Reconcile 结果不隐式恢复原成功输出 | 原始响应缺失时使用 Owner 明确保证的恢复输出或独立 Observation |
| D-28 | Host Context 由单一 Owner Schema 描述 | Host 负责准入及关联校验，Procedure 用显式查询获取动态状态 |
| D-29 | 可选 limits.maxActions | 只允许收紧 Host 强制正数预算，不得增加授权或重试权限 |
| D-30 | Goal PASS 覆盖所有成功路径 | 同一 Goal 可由各分支的 Postcondition 分别证明 |
| D-31 | Predicate 明确声明所需 Evidence 保证 | Compiler 检查绑定，Runtime 验证实际证据 |

# 附录 B：当前状态与待评审事项

本文是可供外部评审的完整设计稿，但仍为 PUBLIC DESIGN REVIEW / NOT FROZEN。

| 项目 | 状态 | 评审责任 |
|---|---|---|
| 术语、概念与职责边界 | 已形成提案 | 架构 / 业务 Owner |
| Procedure 主节点和显式绑定 | 已形成提案 | 语言 / Compiler |
| ToolCatalog typed callable | 候选 YAML，未冻结 | Tool Owner / Compiler |
| CapabilityContracts callable mapping | 候选 YAML，未冻结 | Host / Deployment |
| Observation Query 语法 | 候选表达，待冻结 | Tool Owner / Compiler |
| Evidence 参数要求与 Runtime 校验 | §17 提案；Owner 保证、关联与有效性契约待发布 | Host / Evidence Owner |
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
| Evidence 与 Predicate 参数的关联不明确 | §17 使用参数到保证 ID 的映射；每项至少一条有效证据并校验关联，Runtime 独立确认 | 规则已提出；Owner 保证导出、Host 运行校验与 Fixture 待确认 |
| Predicate Script 类型派生不明确 | Predicate.parameters 是唯一业务输入签名；Script 入口 input: dict 仅为调用容器；Compiler / LSP 必须提供派生只读类型环境 | 语义已明确；生成 stub / overlay 的工具链方式待验证 |
| Schema ID 与路径混淆 | 外部引用使用 dependency-alias::精确 Schema $id；Skill 自有 Schema 使用包内路径；路径不是公共身份 | 规则已明确；需要 Compiler 正负例验证 |
| primitive 类型兼容、nullable 和 CEL 规则不完整 | 由 Compiler 类型兼容矩阵和正负例冻结，未支持关键字不得静默忽略 | 未冻结 |
| 自动同名绑定保留键冲突 | vNext 第一版不支持隐式同名绑定；Studio 可生成显式 arguments | 已纳入本版候选语法 |
| 三个异步 Operation 的 Owner 契约尚未确认 | 责任目标映射到 UPN.CREATE_UP_SESSION、SSM.SIGNAL_UE_AN、UPN.MODIFY_UP_SESSION | 仅为目标责任；ToolCatalog / Output / Evidence 仍待 Owner 确认 |

本附录是评审答复记录，不表示所有问题已实现或已冻结。评审者若不同意某项决定，应指出所影响的术语、语法、静态语义、运行语义或 Owner 边界，并提供正例和反例。

---

# 附录 E：独立的最小链接样例与负例清单

本附录给出一组独立的虚构 Owner 数据，用于评审静态链接和 Runtime 判定。E.1–E.4 的 YAML 及装配规则构成完整的逻辑输入。装配到具体 BuildRequest 线格式属于适配层。这里的 `urn:example` 身份仅用于该用例。

## E.1 Skill 作者源码

~~~yaml
# skills/verify-ue-registration/assurance/contract.yaml
goal: ue.registration_verified
contextSchema: ca-context::urn:example:ca:invocation-context:v1
dependencies:
  ca-context: urn:example:ca:host-context
  ca: urn:example:ca:tools
capabilities:
  - example.registration-read
~~~

~~~yaml
# skills/verify-ue-registration/assurance/procedure.yaml
start: inspect-registration
nodes:
  inspect-registration:
    observation: ca::ue.registration.current
    arguments:
      ueRef: context.ueRef
    'on':
      SUCCEEDED: verify-registration
      FAILED: failed
      UNKNOWN: unresolved

  verify-registration:
    postcondition:
      goal: ue.registration_verified
      predicate: example.ue.registered
      arguments:
        - inspect-registration.output
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

~~~yaml
# skills/verify-ue-registration/assurance/predicates.yaml
predicates:
  example.ue.registered:
    parameters:
      - registration: ca::urn:example:ca:registration:v1
    evidence:
      requires:
        registration: [ca::ue.registration-state]
    evaluator:
      type: cel
      expression: >-
        registration.state == "REGISTERED" &&
        registration.accessState == "ACTIVE"
~~~

## E.2 Host Context 依赖快照

~~~yaml
# invocation-context.schema.yaml（由 ca-context 快照提供）
$id: urn:example:ca:invocation-context:v1
type: object
additionalProperties: false
required: [ueRef]
properties:
  ueRef:
    type: string
    minLength: 1
~~~

## E.3 Observation Tool 依赖快照

~~~yaml
# registration-query.schema.yaml（由 ca 快照提供）
$id: urn:example:ca:registration-query:v1
type: object
additionalProperties: false
required: [ueRef]
properties:
  ueRef:
    type: string
    minLength: 1
~~~

~~~yaml
# registration.schema.yaml（由 ca 快照提供）
$id: urn:example:ca:registration:v1
type: object
additionalProperties: false
required: [state, accessState]
properties:
  state:
    type: string
    enum: [REGISTERED, DEREGISTERED]
  accessState:
    type: string
    enum: [ACTIVE, IDLE]
~~~

~~~yaml
# tool-catalog.yaml（由 ca 快照提供）
apiVersion: connectionagent.io/toolcatalog/v1alpha2
kind: ToolCatalog
metadata:
  name: example-ue-queries
  owner: example-ue-owner
spec:
  contracts:
    - kind: observation
      id: ue.registration.current
      effect: READ
      outcomes: [SUCCEEDED, FAILED, UNKNOWN]
      adapter: example-ue-query
      queryContextSchema:
        $ref: urn:example:ca:registration-query:v1
      outputSchema:
        $ref: urn:example:ca:registration:v1
      guarantees:
        authority: example-ue-owner
        scope: [subject]
        temporal:
          observedAt: required
        evidence:
          provides:
            - guarantee: ue.registration-state
              path: output
~~~

~~~yaml
# evidence-guarantees.yaml（由 ca 快照提供）
ue.registration-state:
  authority: example-ue-owner
  fact: ue.registration
  producers:
    - owner: example-ue-owner
      kind: observation
      id: ue.registration.current
      outcome: SUCCEEDED
      path: output
  scope:
    subject: {record: scope.subject, equals: query.ueRef}
  correlation:
    invocation: {record: invocationId, equals: execution.invocationId}
    producerInvocation: {record: producerInvocationId, equals: execution.producerInvocationId}
  factValue: value
  selection: {mode: latest, orderBy: observedAt}
  freshness: {timestamp: observedAt, maxAgeMs: 10000}
~~~

`query` 表示派发时物化并记录的已校验查询参数；`execution` 表示 Runtime 分配的 Skill Invocation 与 Producer 调用身份。`record` 字段路径读取经过 Owner 验证的证据记录，`factValue` 指参与同事实比较的规范化值。此例以整个 Registration 输出作为该事实值。

## E.4 可信部署授权与 Build 输入

~~~yaml
# capability-contracts.yaml（独立可信部署输入）
apiVersion: connectionagent.io/capability-contracts/v1alpha2
kind: CapabilityContracts
metadata:
  name: example-deployment
spec:
  capabilities:
    - id: example.registration-read
      owner: deployment
      callables:
        - owner: example-ue-owner
          id: ue.registration.current
          kind: observation
          effect: READ
~~~

下列装配描述由可信 Fixture 调用方持有。读取 E.1–E.4 中相同文件名的 YAML 块，去掉用于标记文件名的首行注释，以块中其余字节及换行作为文件内容。对每个 `snapshots` 项，构建调用方按选用的 Compiler 快照摘要规则计算其 `files` 的摘要，将 `dependencyId` 与实测摘要作为同一个快照和可信身份绑定的共同键。每个快照只有一个已验证 Owner，因此该快照内的无 Owner 字段 Schema 归该 Owner。装配描述是本用例的输入，无须在 Owner 快照中新增发布文件。

~~~yaml
# Fixture 逻辑装配描述
skillFiles:
  - skills/verify-ue-registration/assurance/contract.yaml
  - skills/verify-ue-registration/assurance/procedure.yaml
  - skills/verify-ue-registration/assurance/predicates.yaml
capabilityContracts: capability-contracts.yaml
snapshots:
  - dependencyId: ca-context
    packageId: urn:example:ca:host-context
    owners: [example-host-owner]
    files: [invocation-context.schema.yaml]
  - dependencyId: ca
    packageId: urn:example:ca:tools
    owners: [example-ue-owner]
    files: [tool-catalog.yaml, registration-query.schema.yaml, registration.schema.yaml, evidence-guarantees.yaml]
~~~

测试 Host 提供 Invocation Context，测试 Adapter 提供响应与 Evidence。Procedure 仍通过 `arguments.ueRef: context.ueRef` 派发。下方 `observation.arguments` 是测试 Adapter 必须收到的预期实参，由测试夹具比对，不能替换实际绑定。为简化时钟，时间字段使用同一受控时钟的毫秒值。记录在注入时已由对应 Owner 验证，Producer 结果与 Evidence 绑定相同的 `output`。检查 Outcome 时，使用明确给出的校验时间。

~~~yaml
# Fixture 执行输入与预期
invocation:
  id: run-1
  context:
    ueRef: ue-1
  actionBudget: 1
observation:
  producerInvocationId: read-1
  arguments: {ueRef: ue-1}
  outcome: SUCCEEDED
  output: {state: REGISTERED, accessState: ACTIVE}
  evidence:
    ref: record-1
    authority: example-ue-owner
    fact: ue.registration
    scope: {subject: ue-1}
    invocationId: run-1
    producerInvocationId: read-1
    path: output
    observedAt: 1000
    value: {state: REGISTERED, accessState: ACTIVE}
checkedAt:
  observation: 1500
  predicate: 2000
  terminal: 2001
expected:
  predicate: PASS
  terminal: SUCCEEDED
~~~

## E.5 必须存在的正负例

| 场景 | 应产生的结果 |
|---|---|
| E01：上面的全套文件、精确 Owner / Alias / Schema 匹配 | 静态链接 PASS（目标行为，待实现验证） |
| E02：把 procedure.yaml 根加入 goal / capabilities | SOURCE_ROOT_INVALID |
| E03：把 Contract 的 `dependencies.ca` 改成另一个 Package ID | DEPENDENCY_ID_MISMATCH |
| E04：摘要有效，但可信身份绑定缺失，或绑定到另一份快照摘要 | DEPENDENCY_IDENTITY_UNVERIFIED |
| E05：ToolCatalog metadata.owner 不在可信绑定的授权 Owner 中 | DEPENDENCY_OWNER_MISMATCH |
| E06：删除 Contract 的 example.registration-read Grant | CAPABILITY_NOT_GRANTED |
| E07：可信 CapabilityContracts 对同一 Owner、ID 和 kind 的 READ Operation 声明了不同的预期 Effect | EFFECT_MISMATCH |
| E08：Predicate 参数增加一个必填位置参数但不改调用 | PREDICATE_ARITY_MISMATCH |
| E09：把 Predicate 所需 Registration 结构替换成 context.ueRef 字符串 | PREDICATE_TYPE_MISMATCH |
| E10：Reconcile COMMITTED 分支读取原 Mutation 的成功输出，或读取未声明的 Reconcile 输出 | 前者 SOURCE_NOT_AVAILABLE；后者 RECONCILE_OUTPUT_UNAVAILABLE |
| E11：省略所有最终 Postcondition，直接进入 SUCCEEDED | FINAL_POSTCONDITION_MISSING |
| E12：引用 context.ueRef 却未声明 contextSchema | CONTEXT_SCHEMA_UNDECLARED |
| E13：E.4 的 Host Context 缺少必需的 ueRef | ADMISSION_CONTEXT_INVALID，拒绝启动 |
| E14：Host Action Budget 为 0 或非法 | Admission fail-closed，不允许 Skill limits 放宽 |
| E15：Observation 已可从充分 Operation Result 中获得且满足 Evidence 要求 | 不应为了形式强制增加 Observation 节点 |
| E16：未引用的额外 Snapshot 被传入 BuildRequest | 按声明边界链接，额外导出不可访问 |
| E17：正常与 Reconcile 分支的匹配 Goal PASS 汇入同一个 SUCCEEDED | 成功路径覆盖通过 |
| E18：其中一支绕过 Goal PASS；另测 Goal PASS 后再 Mutation、Reconcile、局部或 Goal Predicate 的 FAIL / UNKNOWN | SUCCESS_BYPASSES_FINAL_POSTCONDITION |
| E19：相同 Payload Schema 的 Producer 缺少参数要求的保证 | PREDICATE_EVIDENCE_UNSATISFIABLE |
| E20：多保证参数缺一条有效记录；另测错误 Owner、错 PSI / Lifecycle、过期、同 Scope 冲突 | UNKNOWN，即使业务值使 evaluator 返回 PASS |
| E21：所有保证有效，Script 返回 PASS 且 evidenceUsed 为空；另测其引用未附加 Ref | 前者 PASS 并由 Runtime 记录支撑证据；后者 UNKNOWN |
| E22：无安全 Reconcile 契约时，UNKNOWN 进入新 Mutation；另测正确安全终止 | 前者阻断构建；后者保留原调用与迟到结果责任 |
| E23：RAN 已完成，Forwarding 失败或不确定 | SAFE_STOPPED，保留资源句柄、责任与停止原因 |
| E24：存在入口门禁，一条路径跳过 PASS 就派发 Mutation | ENTRY_PRECONDITION_BYPASSED |
| E25：Host Context Schema 声明保留属性 request | CONTEXT_REQUEST_COLLISION |
| E26：Reconcile 已提交但只能按 UE 查询另一个同 DNN 订阅；另测按已恢复的精确资源 Ref 查询 | 前者无法满足当前资源关联，不能 PASS；后者仍须通过类型、Evidence 与资源责任检查 |
| E27：入口证据在第二次 Mutation 前到达有效期上界 | 不派发第二次 Mutation；按已知部分完成和提交状态决定终态 |
| E28：Mutation 回包损坏，有 / 无独立有效提交证明 | 有证明则 COMMITTED_OUTPUT_UNAVAILABLE、SAFE_STOPPED；无证明则沿 OUTCOME_UNKNOWN |
| E29：Reconcile UNRESOLVED，有 / 无已知部分资源 | 前者 SAFE_STOPPED，后者 UNRESOLVED；均保留原调用责任 |
| E30：同一注册事实收到更新且不同值的权威记录；另测同序不同值 | 旧绑定在两种情况下均不能 PASS。前者须显式绑定新 Producer 才可按新值判断；后者 UNKNOWN |
| E31：E.4 的 terminal 校验时间改为 11000 | 先前 Predicate PASS 保留在 Trace 中，实际终态 UNRESOLVED |
| E32：不同证据 Ref 指向同一底层记录，但 Predicate 要求两个独立来源 | UNKNOWN |
| E33：Reconcile 已确认提交但其承诺恢复的资源 Ref 无效 | 保留已提交状态并 SAFE_STOPPED，后续节点不可读取该 Ref |
| E34：Procedure 使用旧的根字段 inputs，或以 input.ueRef 绑定参数；另测节点 ID 为 context | 分别拒绝未知根字段、非法 SourcePath 和保留节点名 |
| E35：Contract 使用 `allowedResources` 包装，或用对象作为 `dependencies.ca` 的值 | 分别为 UNKNOWN_FIELD 和 DEPENDENCY_REQUIREMENT_INVALID |
| E36：调用实参使用不匹配 SourcePath 的裸字符串 | SOURCE_PATH_INVALID |
| E37：SourcePath 直接读取 Producer Schema 中可缺失的字段 | SOURCE_NOT_AVAILABLE |
| E38：`provides` 引用不存在的保证 ID | EVIDENCE_GUARANTEE_LINK_INVALID |
| E39：多 Owner 快照缺少某个实际链接的导出归属 | DEPENDENCY_EXPORT_OWNER_UNVERIFIED |
| E40：较新的可信记录与旧绑定同值，但版本已取代旧绑定 | Trace 保留先前 PASS，终态 UNRESOLVED |
| E41：首节点是 Goal Postcondition | 只有该节点的 PASS 边建立证明 |
| E42：局部 Postcondition PASS 之后进入成功终态 | 已有证明则保持；无 Goal Postcondition 则报 FINAL_POSTCONDITION_MISSING |
| E43：多 Owner 快照中已有唯一归属，但 Owner 越权 | DEPENDENCY_OWNER_MISMATCH |
| E44：不可达节点有一条指向可达成功终态的边 | UNREACHABLE_NODE 警告；该边不影响证明 |
| E45：Goal PASS 后经过入口 Precondition，再尝试成功 | SUCCESS_BYPASSES_FINAL_POSTCONDITION，入口 PASS 清除旧证明 |
| E46：Observation 的保证描述符误用 Operation 的实参引用根 | EVIDENCE_GUARANTEE_LINK_INVALID |

此表是待落地的评审与 Compiler Fixture 契约，不是现有 CI 的实际通过记录。正式冻结必须由相应 Owner 提供发布的导出身份，并让 Native、WASM 和 Skill Studio 使用同一组正负例。

## E.6 基于独立样例的最小变更

除 E07、E39 和 E43 使用各自注明的正例基线外，每行独立从 E.1–E.4 的成功输入开始，按逻辑输入路径应用变更。修改快照文件时，除非该用例测试摘要或可信绑定失败，应重新计算该快照摘要并重新绑定其原可信身份，避免在目标诊断前被摘要检查拦截。路径中的 `contract`、`procedure`、`predicates` 指 E.1 的三个文件。`catalog` 和 `guarantees` 分别指 E.3 的 ToolCatalog 和保证描述符。`deployment` 指 E.4 的可信 CapabilityContracts。

E07 的 READ Operation 基线：将 `procedure.nodes.inspect-registration` 的 `observation` 键改为 `operation`，将 `catalog.spec.contracts[0]` 的 `kind` 改为 `operation`、`queryContextSchema` 键改为 `inputSchema`，并将 `guarantees["ue.registration-state"].producers[0].kind` 与 `deployment.spec.capabilities[0].callables[0].kind` 同步改为 `operation`。Producer 调用实参的证据绑定改用 `arguments.ueRef`；它与 Observation 的 `query.ueRef` 均读取已物化的同一调用实参。校验这一基线应通过链接，再修改部署侧 Effect。

| 用例 | 最小改动 | 预期 |
|---|---|---|
| E02 | 在 `procedure.goal` 写入 `ue.registration_verified` | SOURCE_ROOT_INVALID |
| E03 | 将 `contract.dependencies.ca` 改为 `urn:example:ca:other-tools` | DEPENDENCY_ID_MISMATCH |
| E04 | 删除 ca 快照按别名和摘要建立的可信绑定 | DEPENDENCY_IDENTITY_UNVERIFIED |
| E05 | 将 `catalog.metadata.owner` 改为 `example-untrusted-owner` | DEPENDENCY_OWNER_MISMATCH |
| E06 | 将 `contract.capabilities` 改为空列表 | CAPABILITY_NOT_GRANTED |
| E07 | 从表前的 READ Operation 正例开始，将 `deployment.spec.capabilities[0].callables[0].effect` 改为 MUTATION | EFFECT_MISMATCH |
| E08 | 在 `predicates.predicates["example.ue.registered"].parameters` 追加 `{second: string}` | PREDICATE_ARITY_MISMATCH |
| E09 | 将 `procedure.nodes.verify-registration.postcondition.arguments[0]` 改为 `context.ueRef` | PREDICATE_TYPE_MISMATCH |
| E12 | 删除 `contract.contextSchema` | CONTEXT_SCHEMA_UNDECLARED |
| E13 | 删除执行输入的 `invocation.context.ueRef` | ADMISSION_CONTEXT_INVALID |
| E19 | 删除 `catalog.spec.contracts[0].guarantees.evidence.provides` | PREDICATE_EVIDENCE_UNSATISFIABLE |
| E25 | 在 Host Schema 的 `properties` 加入 `request: {type: object}` | CONTEXT_REQUEST_COLLISION |
| E31 | 将 `checkedAt.terminal` 改为 11000 | Trace 保留 PASS，终态 UNRESOLVED |
| E35 | 将 `contract.dependencies.ca` 替换为 `{id: urn:example:ca:tools}` | DEPENDENCY_REQUIREMENT_INVALID |
| E36 | 将 `procedure.nodes.inspect-registration.arguments.ueRef` 改为裸字符串 `ue-1` | SOURCE_PATH_INVALID |
| E37 | 在 Registration 输出 Schema 的 `properties` 加入 `reason: {type: string}`，保持其可选，并将 `procedure.nodes.verify-registration.postcondition.arguments[0]` 改为 `inspect-registration.output.reason` | SOURCE_NOT_AVAILABLE，先检查路径可用性再检查类型 |
| E38 | 将 `catalog.spec.contracts[0].guarantees.evidence.provides[0].guarantee` 改为 `ue.missing` | EVIDENCE_GUARANTEE_LINK_INVALID |
| E39 | 从表后的多 Owner 正例开始，删除 Registration 输出 Schema 的归属 | DEPENDENCY_EXPORT_OWNER_UNVERIFIED |
| E43 | 从同一个多 Owner 正例开始，将 Registration 输出 Schema 的唯一归属改为 `example-untrusted-owner` | DEPENDENCY_OWNER_MISMATCH |
| E46 | 将 `guarantees["ue.registration-state"].scope.subject.equals` 从 `query.ueRef` 改为 `arguments.ueRef` | EVIDENCE_GUARANTEE_LINK_INVALID |

E39、E43 的 ca 快照基线：将可信 Owner 集合设为 `[example-ue-owner, example-other-owner]`，并在可信身份绑定中为实际链接的导出声明下表的归属。保留原有文件和摘要，先校验多 Owner 输入可以链接，再分别应用 E39 或 E43 的改动。表格描述逻辑绑定，具体 BuildRequest 线格式按 §34.0 确定。

| exportKind | exportId | owner |
|---|---|---|
| observation | ue.registration.current | example-ue-owner |
| schema | urn:example:ca:registration-query:v1 | example-ue-owner |
| schema | urn:example:ca:registration:v1 | example-ue-owner |
| evidenceGuarantee | ue.registration-state | example-ue-owner |

## E.7 控制流与证据复核变体

| 用例 | 基线与最小改动 | 预期 |
|---|---|---|
| E17 | §12.1 的正常与 Reconcile 路径，各自通过 Goal Postcondition 后汇入 complete | 静态证明覆盖检查通过 |
| E18 | 将 §12.1 的 `reconcile-subscription.on.COMMITTED` 从 `inspect-after-reconcile` 改为 `complete` | SUCCESS_BYPASSES_FINAL_POSTCONDITION，即使另一条入边已持有 Goal PASS |
| E10 | 将 §12.1 的 `inspect-after-reconcile.arguments.subscriptionRef` 改为 `create-subscription.output.subscriptionRef`，并让原 Mutation 的 SUCCEEDED 输出 Schema 声明必需的 `subscriptionRef` | SOURCE_NOT_AVAILABLE，当前分支没有该 SUCCEEDED 输出。若该 Schema 未声明此字段，则按 §13.3 报 SOURCE_PATH_INVALID |
| E41 | `start` 指向 E.8 的 `verify-subject`，它的 PASS 直接到 `complete` | Goal 覆盖通过。初始无证明，PASS 建立证明 |
| E42 | 在 E.8 的 `verify-subject` PASS 后插入 `verify-local`，使用同一 Predicate 和实参，省略 `goal`，PASS 到 `complete`。再单独移除 `verify-subject` 的 `goal` | 有 Goal 标记时通过。两个判断都无 Goal 标记时报告 FINAL_POSTCONDITION_MISSING |
| E44 | 在 E.8 增加一个从 `start` 不可达的节点 `unused`，声明 `precondition.predicate: example.subject.present`、实参 `context.ueRef`，其 PASS 到 `complete`，FAIL 到 `failed`，UNKNOWN 到 `unresolved` | 报 UNREACHABLE_NODE；`complete` 的证明覆盖仍通过 |
| E45 | 在 E.8 的 `verify-subject` PASS 后插入一个 `entry: true` 的 Precondition，使用同一 Predicate 和实参，PASS 到 `complete`，其余边到相应停止终态 | SUCCESS_BYPASSES_FINAL_POSTCONDITION |
| E30、E40 | 在 E.4 的 Predicate PASS 之后、终态复核前，加入同一 Invocation 下另一条已由 Owner 校验的证据，`ref: record-2`、`producerInvocationId: read-2`、`observedAt: 1800`，其已物化查询实参仍为 `ue-1`。E30 使用 `{state: DEREGISTERED, accessState: IDLE}`；E40 使用与 record-1 相同的值。此处只向测试 Host 的证据视图注入 Owner 记录 | 原绑定的 PASS 保留在 Trace，终态 UNRESOLVED。两种情况下均不得换绑或重新调用 Predicate |

## E.8 从 Goal Postcondition 开始的验证流程

复用 E.2 的 Host Schema 和 E.4 的 Invocation Context。此例的 Contract 只需 `goal: ue.subject_verified`、E.1 的 `contextSchema` 以及 `ca-context` 的依赖声明。该 Goal 只验证已准入的 UE 引用非空。

~~~yaml
# assurance/procedure.yaml
start: verify-subject
nodes:
  verify-subject:
    postcondition:
      goal: ue.subject_verified
      predicate: example.subject.present
      arguments:
        - context.ueRef
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

~~~yaml
# assurance/predicates.yaml
predicates:
  example.subject.present:
    parameters:
      - ueRef: string
    evaluator:
      type: cel
      expression: ueRef != ""
~~~

---

**规范结束。**
