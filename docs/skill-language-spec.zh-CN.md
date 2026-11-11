# ConnectionAgent Skill 语言规范

**版本：** v0.1  
**状态：** Draft——基于当前源码整理的语言契约，尚不代表 Compiler 一致性验收通过  
**归属：** `ca-skills`  
**消费者：** `ca-skill-compiler`、`ca-skill-studio-demo`，以及未来的 LSP

本文档扩展现有编写指南中的 **One CA Authoring Language Core**，明确当前源码使用的语法词汇、Artifact 边界、引用关系和语义 Token 分类，不另造一套 DSL。

## 1. 权威边界与范围

`ca-skills` 负责 Authoring Semantics 和对外的 Skill 源码语言契约。本文是以下内容的规范来源：

- 官方 Skill 源码构造的含义和作用；
- 语言关键字、用户自定义标识符与引用的区别；
- 编辑器和未来语言服务共用的稳定语义 Token ID；
- 当前源码语法、已有文档但尚未验证的语法、未来设计之间的边界。

目标 Compiler 实现这份契约并提供机器校验；Skill Studio 消费 Token 分类实现语法高亮；未来 LSP 可以复用同一套符号和引用分类，实现诊断、补全、定义跳转和引用查找。

旧版 `ca-skill-toolchain` Schema 只验证它实际建模的子集，不能反过来重新定义或静默缩小当前源码契约。尤其是传统 PDU Session Skill 已使用节点级 `preconditions` 和 `postconditions`，而旧版 Procedure Schema 不支持这些字段。目标无状态 Compiler 必须实现已记录的源码语义，或者明确报告不支持的语法；绝不能静默丢弃。

本 v0 根据当前两个 5GC Skill 和导入的 Library 快照整理，不代表新 Compiler、Linker 或 Runtime 已接受或执行所有构造。

## 2. 语言层次

Skill 编写语言由现有格式与 ConnectionAgent 专属结构组合而成：

| 层次 | 源文件 | 语言职责 |
| --- | --- | --- |
| 模型指导 | `SKILL.md` | Markdown 与标准 Skill frontmatter；描述业务含义、适用范围和安全边界 |
| Skill 契约 | `assurance/contract.yaml` | Skill 身份、目标、入口 Procedure、资源边界和最终条件 |
| Procedure | `assurance/procedure.yaml` | 确定性流程图、节点意图、绑定、条件和结果路由 |
| Predicate 集合 | `assurance/predicates.yaml` | 必需 Observation，以及基于已物化 Evidence 的确定性判断 |
| 资格 Case | `cases/<case>/case.yaml` | 场景、Fixture 和预期语义义务 |
| 受治理脚本 | `scripts/*.py` | 带有声明元信息和 Schema 的确定性本地计算 |
| Skill Schema | `schemas/*` | Skill 自有的 Payload/Schema；JSON Schema 关键字仍属于 JSON Schema，不是 CA 关键字 |
| 补充知识 | `references/*.md` | 可选 Markdown 知识，不是可执行语法，也不是 Evidence |
| 导入 Library | `lib/**/*.yaml` | 只读外部契约/目录，由 Skill 源码引用 |
| 生成产物 | `output/**` | Compiler 所有的生成结果，不能作为源码输入 |

不能把所有 YAML key 都当作保留字。YAML 是序列化格式；只有出现在已定义 ConnectionAgent 语法位置的 Key/Value 才获得 CA 语义分类。

## 3. 当前 Artifact 形式

下面列出当前源码基线中实际存在、或现有编写参考明确记录的字段和形式。它们不代表所有旧版 Schema/Compiler 都接受这些语法。字段的精确必填性和约束由目标机器 Schema 定义。

### 3.1 `SKILL.md`

Frontmatter 使用标准 Skill 元信息字段 `name` 和 `description`。Markdown 正文是面向模型的业务说明。标题和普通领域词汇不是 CA 保留关键字。

### 3.2 `SkillContract`

当前文档身份：

```yaml
apiVersion: connectionagent.io/v1alpha1
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
    requiredFacts: []
  allowedResources:
    capabilities: []
    localTools: []
  postconditions: []
```

当前编写模型识别的结构字段包括：

- `skillType`、`goal`、`entryProcedure`；
- `inputs.requestSchema`；
- `context.requiredFacts`；
- `allowedResources.capabilities` 和 `allowedResources.localTools`；
- Contract 级 `preconditions`、`requirements` 和 `postconditions`；
- `planning.maxActions`、`planning.allowDynamicProcedure`；
- `failureSemantics.outcomeUnknown.requireReconcile`。

Contract 级 preconditions/postconditions 是整个 Skill 的条件，不等同于 Procedure 节点级的 preconditions/postconditions。

### 3.3 `Procedure`

当前源码采用对象形式的流程图：

```yaml
procedures:
  <procedure-id>:
    inputs: {}
    start: <node-id>
    nodes:
      <node-id>:
        call: capability.operation
        with: {}
        'on': {}
```

当前 5GC 源码使用的节点意图：

| Intent Key | 含义 |
| --- | --- |
| `call` | 调用被引用的受治理 Capability/Operation |
| `verify` | 判断被引用的 Predicate |
| `script` | 执行受治理的本地计算脚本 |
| `reconcile` | 调和原始的、具有不确定结果的变更节点 |
| `terminal` | 以声明的 Procedure 终态结束 |

早期语法参考还记录了 `tool`、`procedure` 和 `for` 形式。它们属于**已有文档描述、但当前两个 5GC Skill 尚未使用验证**的语法；在被视为通用可用语法前，必须确认目标 Compiler 的支持情况。迭代必须显式有界，并受 Artifact 类型约束。

Procedure 可以声明：

- `inputs.<name>.type` 和 `inputs.<name>.from`；
- `start` 和 `nodes`；
- `with.<argument>.from` 或 `with.<argument>.value`；
- `'on'` 结果到下一节点的映射；
- `applicability`；当前传统 PDU Session 源码使用其中的 `predicates` 映射；
- 节点级 `preconditions` 和 `postconditions`。

不要把节点 ID、输入名、参数名或输出字段名误认为保留关键字。它们都是作者定义的标识符。

### 3.4 节点级 Preconditions 和 Postconditions

传统 PDU Session 源码使用带有 `steps` 和 `'on'` 结果映射的有序阶段：

```yaml
preconditions:
  steps:
    - name: prepare-input
      script: scripts/prepare_input.py
  'on':
    PASS: continue
    FAIL: failed
    UNKNOWN: unresolved

postconditions:
  steps:
    - verify: example.operation_effective
  'on':
    PASS: next-business-node
    FAIL: failed
    UNKNOWN: unresolved
```

Preconditions 是主操作前立即执行的无副作用准备；Postconditions 在 Procedure 继续前证明操作的业务结果。具体执行顺序和失败语义见[Authoring Model](authoring-model.md)。

这些节点级字段已经存在于当前源码，但旧版 `ca-skill-toolchain` Procedure Schema 不支持。它们属于目标源码契约，不意味着可以自行发明其他节点字段。

### 3.5 Binding 与 Path

每个 `with` 参数只能有一种显式来源：

- `from`：引用 Procedure 输入、准入上下文、前序节点结果或准备阶段结果；
- `value`：字面量。

当前 Path 命名空间包括 `input.*`、`context.subject.*`、`context.request.*`、`context.facts.*`、`context.constraints.*`、迭代得到支持时的 `loop.*`，以及明确的生产者路径，例如 `<node>.output.*` 或 `<node>.preconditions.<step>.output`。

Path 不是任意字符串表达式。不要发明隐式前序节点绑定、隐藏插值、`fromContext` 或 `fromOutput`。

### 3.6 Predicate 集合

当前文档身份：

```yaml
apiVersion: connectionagent.io/v1alpha1
kind: PredicateSet
metadata:
  skill: establish-pdu-session
predicates:
  example.goal_satisfied:
    observations:
      state:
        ref: example.state.snapshot
        scope: '{}'
        freshness: 5s
    evaluator:
      type: cel
      expression: observations.state.status == "READY"
```

当前源码词汇包括：

- `predicates.<predicate-id>` 定义；
- `observations.<alias>.ref`、`scope` 和 `freshness`；
- `evaluator.type`，当前源码形式为 `cel` 和 `script`；
- CEL 使用 `evaluator.expression`，受治理的 Predicate Script 使用 `evaluator.ref`。

Expression 的值属于 CEL 子语言，不是 YAML 或 CA 关键字列表。Predicate 只判断已经物化的 Evidence，不负责获取 Evidence 或调用 Provider。

### 3.7 资格 Case

每个 Case 是一个独立的 `cases/<case-name>/case.yaml` 文件，文档身份为 `kind: SkillTestCase`。当前源码字段包括 `metadata.skill`、`metadata.name`、`spec.classes`、`spec.purpose`、`spec.context`、`spec.expect` 和 `spec.fixtures`。

Case 是源码层面的语义义务。文件存在不代表它已执行、不代表 Runtime 已通过，也不代表 Skill 已取得资格。

### 3.8 受治理 Python Script

Skill 内 Python Script 只负责确定性本地计算。文档化的元信息块由 `# /// connectionagent-tool` 分隔，字段包括 `name`、`inputSchema`、`outputSchema`、`effect`、`sandbox.network` 和 `timeout` 等。

Script 元信息不是普通 Python 语法。Script 正文仍由 Python 语言工具处理；CA Token 分类只作用于元信息块，以及 Skill 对 Script 的引用。

### 3.9 导入的 ToolCatalog 与 Capability 引用

当前导入快照是 `lib/tools/createdsession.tool.yaml`，其文档类型为 `ToolCatalog`。Operation 定义位于 `spec.contracts[].operation`，并带有对应的 adapter、effect、input schema 和 output schema。

当前传统 Skill 中：

- `contract.spec.allowedResources.capabilities[]` 声明 Skill 可以使用的 Capability ID；
- Procedure 的 `call` 值引用这些业务/Runtime Operation ID；
- 导入的 ToolCatalog 定义相应的 Operation 身份。

当前基线中，传统 Skill 的 12 个 Capability 引用均可按精确 Operation 名称解析。MAS Skill 声明的 16 个 `ca.pdu_session.*` 引用不在该目录中，因此仍是未解析引用；不得自行编造定义，也不能把 MAS 设计稿当成已批准的导入契约。

导入解析成功只代表源码/链接层面的事实，不代表实现已注册、已部署、READY、已授权或成功执行。

## 4. 符号与引用模型

以下定义/引用关系构成 v0 的跳转契约。机器可读的 Token ID 和源码选择器统一记录在[语义 Token 目录](../spec/skill-language-tokens.yaml)：

| 定义 | 定义位置 | 引用位置 |
| --- | --- | --- |
| Skill | Skill 包 frontmatter 的 `name` | Case 的 `metadata.skill`；其他明确声明的包级引用 |
| Procedure | `procedure.yaml: procedures.<id>` Map Key | Contract 的 `entryProcedure`；受支持的子 Procedure 引用 |
| Procedure Node | `procedure.yaml: procedures.*.nodes.<id>` Map Key | `start`、主节点 `'on'` 目标、`reconcile` 目标 |
| Predicate | `predicates.yaml: predicates.<id>` Map Key | Procedure 的 `verify`；Contract 的 `predicate` 字段；`applicability.predicates` |
| Operation | 导入 ToolCatalog 的 `spec.contracts[].operation` | Contract 的 `allowedResources.capabilities[]`；Procedure 的 `call` |
| Case | `case.yaml: metadata.name` | Case 的 `metadata.skill` 标识所属 Skill |
| Local Tool | Script 元信息身份（与 `skill.*` local-tool ID 的映射尚未冻结） | Contract 的 `allowedResources.localTools[]`；受支持时的 Procedure `tool`；指向 Local Tool 的 Predicate evaluator `ref` |
| Script | `scripts/` 下的文件 | Procedure 的 `script` 路径 |
| Schema | `schemas/` 下的文件 | Contract 的 `requestSchema`；其他按路径引用的 Schema |

解析规则：

1. 只允许精确标识符和包内相对路径，不做模糊名称匹配。
2. Operation 引用必须针对项目选定的导入目录解析；不能假设所有 Capability 都定义在同一个目录中。
3. `reconcile` 必须解析到同一 Procedure 中原始的变更节点，不是 Capability 引用。
4. 未解析引用必须保留为未解析状态。语法高亮不能暗示链接已经成功。
5. 出现在正文、注释、用户自定义 Map Key 或无关 YAML 字段中的同名字符串，不自动成为符号引用。

这些关系定义未来的 Go-to-Definition 和 Find References 行为。第一阶段可以只根据语法位置分类引用，不要求解析目标文件。

## 5. 语义 Token 分类

以下 Token ID 是稳定的语言级分类，独立于编辑器主题颜色，也独立于未来 LSP 对 Semantic Token Type 的编码。

| Token ID | 适用位置 | 示例 |
| --- | --- | --- |
| `ca.document.kind` | 文档 `kind` 的值 | `SkillContract`、`PredicateSet`、`SkillTestCase`、`ToolCatalog` |
| `ca.document.version` | `apiVersion` 的值 | `connectionagent.io/v1alpha1` |
| `ca.keyword.structure` | 定义位置中的 CA 结构字段 | `spec`、`metadata`、`procedures`、`nodes`、`predicates`、`observations` |
| `ca.keyword.control` | 节点意图 Key | `call`、`verify`、`script`、`reconcile`、`terminal` |
| `ca.keyword.condition` | 条件/阶段 Key | `applicability`、`preconditions`、`postconditions`、`steps`、`'on'` |
| `ca.keyword.binding` | 绑定 Key | `with`、`from`、`value` |
| `ca.reference.capability` | Capability 引用值 | `sbi.udm.sm_data.get` |
| `ca.symbol.skill-definition` | Skill frontmatter name | `name: establish-pdu-session` |
| `ca.symbol.procedure-definition` | Procedure 定义 Map Key | `procedures.<id>` |
| `ca.symbol.node-definition` | Procedure Node 定义 Map Key | `nodes.<id>` |
| `ca.symbol.predicate-definition` | Predicate 定义 Map Key | `predicates.<id>` |
| `ca.symbol.case-definition` | Case 的 `metadata.name` | `01-complete-profile` |
| `ca.symbol.local-tool-definition` | Script 元信息中的 Local Tool 身份 | `# name: select-establishment-configuration` |
| `ca.symbol.operation-definition` | 导入 Operation 定义值 | `spec.contracts[].operation` |
| `ca.reference.predicate` | 引用位置中的 Predicate ID | `createdsession.ingress.eligible` |
| `ca.reference.procedure` | 引用位置中的 Procedure ID | `entryProcedure`、子 Procedure 引用 |
| `ca.reference.node` | 引用位置中的 Procedure Node ID | `start`、主节点 `'on'` 目标、`reconcile` 目标 |
| `ca.reference.local-tool` | 引用位置中的 Skill Local Tool ID | `skill.select-establishment-configuration` |
| `ca.reference.script` | 包内相对 Script 路径 | `scripts/select_establishment_configuration.py` |
| `ca.reference.schema` | 包内相对 Schema 路径或 Schema Registry 引用 | `schemas/establishment-request.schema.yaml` |
| `ca.reference.binding-path` | `from` 的值 | `input.ue`、`context.request.dnn` |
| `ca.value.outcome` | 结果映射/期望中的 Outcome | `PASS`、`UNKNOWN`、`COMMITTED`、`OUTCOME_UNKNOWN` |
| `ca.value.effect` | Tool/Case 契约中的 Effect 值 | `READ`、`MUTATION`、`local_compute` |
| `ca.value.type` | 类型声明中的基础类型值 | `string`、`integer`、`object` |
| `ca.expression.cel` | CEL Expression 值 | `observations.state.status == "READY"` |
| `ca.identifier.user-defined` | 用户定义的 ID 和 Map/Property 名称 | Node ID、输入名、Observation Alias、Case 名称 |

普通 YAML/Python 注释继续由各自的语言 Grammar 处理，不属于 CA 专属语义 Token。分类必须依赖语法位置，不能只依赖拼写。例如，只有作为节点意图 Key 的 `call` 才是控制关键字；正文或用户自定义字段中的同名文本是普通文本。只有位于 `allowedResources.capabilities` 或 Procedure `call` 值中的 Capability ID 才是引用。任意属性 `status` 不是 CA 保留 Token。

Outcome 值由各自的结果域负责：

- Predicate Outcome：`PASS`、`FAIL`、`UNKNOWN`；
- Procedure 终态：`SUCCEEDED`、`FAILED`、`UNRESOLVED`、`SAFE_STOPPED`；
- Operation Outcome：由被引用的 Operation 契约声明，不存在一个全局硬编码枚举。

Effect 值也取决于声明它的契约。不要把 `READ`、`read_only`、`MUTATION` 和 `local_compute` 合并成自行发明的统一枚举。

机器可读的 Token ID 注册表位于 `spec/skill-language-tokens.yaml`，记录 Token ID、源码位置和符号/引用选择器，不包含编辑器专属颜色。Token 分类定义的是**它是什么**，不是**它显示什么颜色**。颜色映射由 Skill Studio 的主题负责。未来 LSP Semantic Tokens 必须复用相同 Token ID，不能再创建一套 Studio 专属词汇。

## 6. 当前、待确认与排除的语法

| 构造 | 当前源码状态 | Compiler 状态/规则 |
| --- | --- | --- |
| Skill frontmatter、Contract、Procedure 图、PredicateSet、Case Envelope | 当前包基线中存在 | 按目标源码契约校验 |
| Procedure 的 `call`、`verify`、`script`、`reconcile`、`terminal` | 当前 5GC 源码中存在 | 必须识别并实现 |
| 节点级 `preconditions` / `postconditions` | 传统源码中存在 | 旧版 Toolchain 不支持；目标 Compiler 必须支持 |
| `applicability.predicates` | 传统源码中存在 | 保留这一已观察到的形式 |
| `applicability.when` | 出现在较早的编写示例中，不在当前两个包的基线中 | v0 不冻结；不能与 `predicates` 视为等价 |
| Procedure `tool`、子 `procedure`、`for` | 早期语法文档有描述，当前两个包没有展示 | 声称支持前必须确认目标 Compiler 语义 |
| `rules.yaml`、`SkillRuleSet`、`ruleRefs` 等 Rule 源码 | 仅设计阶段，当前 Skill 包不存在 | 排除在 v0 语法和保留关键字高亮之外 |
| Rule 的 `path / op / value` | 长期 Language Core 的候选原语 | 当前不是保留语法 |
| MAS Capability 引用 | MAS 源码中声明，但导入 ToolCatalog 不包含 | 按引用着色；导入批准前保持 unresolved |

## 7. 编辑器与 LSP 消费方式

### 第一阶段：Skill Studio 高亮

Skill Studio 可以使用 YAML/TextMate 上下文规则，为这些 Token ID 分配带命名空间的 TextMate Scope，并映射到现有 Studio 主题。必须做到：

- 保留普通 YAML 语法高亮；
- 只在定义好的结构位置识别 CA 关键字；
- 根据字段上下文识别 Capability、Predicate、Procedure、Script 和 Schema 引用；
- 让用户自定义标识符与保留语法有视觉区分；
- 不通过颜色暗示引用解析、语义校验或 Runtime 就绪。

第一阶段不要求实现 LSP Server、诊断、补全或跳转。

### 后续：LSP 与 Compiler

Compiler 解析并校验源码契约，建立符号/引用索引。LSP 消费该索引及同一套 Token 分类，实现 Semantic Tokens、诊断、补全、Go-to-Definition 和 Find References。Compiler 不得依赖 Skill Studio、TextMate 或主题配置。

## 8. 变更控制与未决事项

新增保留字、Artifact 类型、节点意图、绑定形式、表达式语言或引用规则，必须：

1. 更新本文，给出示例和明确的支持状态；
2. 增加正例与负例源码 Fixture；
3. 更新目标 Compiler 的实现和校验；
4. 同步 Skill Studio Grammar/Token；
5. 同步中英文编写指南。

以下内容有意不在 v0 冻结：Rule 机器语法；`applicability.when` 的精确语义；通用子 Procedure 和迭代支持；跨项目 Capability/Operation Registry 的完整定义与版本解析契约。不得用编辑器专属猜测填补这些缺口。

相关文档：

- [Skill 编写指南](authoring.zh-CN.md)
- [Authoring Guide](authoring.md)
- [Authoring Model](authoring-model.md)
- [实用语法参考](../.agents/skills/create-connectionagent-skill/references/authoring-syntax.md)
- [当前 5GC 源码基线](current-5gc-skill-baseline.md)
