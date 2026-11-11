# ConnectionAgent Skill 编写指南

本文面向官方 Skill 的作者，说明当前 `ca-skills` 源码模型。它是实践指南，不是机器语法的第二份权威副本。

当前两个 5GC Skill 及其验证边界见[当前 5GC Skill 基线](current-5gc-skill-baseline.md)。项目根目录权限以及 `skills/` / `lib/` / `output/` 模型见[项目目录规范](project-layout.md)。Procedure 节点准备阶段与验证阶段的语义见[Authoring Model](authoring-model.md)。

## 1. 先判断资产类型

- **可执行 Skill：** 拥有明确业务目标和确定性保障流程。使用 `SKILL.md`、完整的 `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` 三件套，以及语义 Case。
- **模型上下文 / 路由策略包：** 为 Agent 提供业务语义，但自身不定义 Runtime Procedure。
- **Capability / Tool Contract：** 定义一个受治理的操作及其输入、输出和 Effect 契约。不要仅仅为了包装或重名单个底层操作而创建 Skill。

## 2. 标准目录

可执行 Skill 通常采用：

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/       # 可选，平铺 Markdown
├── schemas/           # 可选，Skill 自己拥有的 payload schema
└── scripts/           # 可选，受治理的本地确定性计算
```

不要创建空目录、包根目录 `README.md` / `MIGRATION.md`、`examples/` 或维护者专用的 `design/`。

## 3. 编写面向模型的 SKILL.md

`SKILL.md` 只保留会影响模型业务决策的信息：

- Skill 的适用条件与支持的 profile；
- 业务目标和必须建立的事实；
- 输入归一化与消歧；
- 模型不得作出的推断；
- 业务完成、失败与不确定性语义。

不要把确定性 Procedure 图复制成 prose 流程。不要把 Host/Runtime 内部机制、Adapter 名称、Provider/Fabric 拓扑、部署 endpoint、凭据或传输实现细节放进模型上下文。维护者需要的集成说明放在仓库 `docs/` 下。

模型响应、Action acknowledgement 或传输成功都不能代替独立业务事实。

## 4. References

使用平铺的 `references/*.md`。在 `SKILL.md` 中列出精确路径，并说明每份材料适合解决什么问题。Reference 是可选知识，由模型根据当前决策自行选择；不要创建 `preload/` 或 `on-demand/` 子目录，也不要通过目录名表达加载策略。

Reference 是补充知识，不是实时 Evidence、授权或第二套执行图。

## 5. Assurance 与 Procedure

可执行 Skill 的 `assurance/` 必须完整存在或完全不存在：

- `contract.yaml`：定义 Skill 目标、资源边界、前置条件和最终后置条件；
- `procedure.yaml`：定义确定性流程、数据绑定和 Outcome 路由；
- `predicates.yaml`：定义 Evidence 要求和确定性判断。

当前 5GC 源码还使用 Procedure 节点级 `preconditions` 和 `postconditions`。其执行顺序和 Outcome 语义见[Authoring Model](authoring-model.md)。不要为了通过旧版 Toolchain Schema 而删除这些字段：当前旧版 `procedure-source.schema.yaml` 尚未建模它们。

## 6. Cases

每个 Case 使用一个 `cases/<case>/case.yaml`。Case 表达语义义务。源码 Case、Schema 校验或手写 expected 结果，都不代表 Runtime 或资格测试已经执行。

传统 PDU Session Skill 有 36 个语义义务；其 `cases/README.md` 明确说明这些尚不是可执行 Runtime fixture。

## 7. Scripts 与 Schemas

Skill 内 Python Script 是受治理的本地确定性计算，可以归一化、选择、派生或判断已提供的数据。不得调用 Provider、MCP Server、网络、Shell 工作流、时钟、数据库或凭据。

Skill 自有 Schema 放在 `schemas/`。不要从任意 Python 函数体猜测约束。未来 Compiler 只能生成明确声明可推导的部分；无法推导的约束仍以作者维护的 Schema 为准。

## 8. 导入的 Tool Contract

外部 Tool Contract 作为只读快照放在项目 `lib/` 下。不要手工修改导入文件，也不要把同一份外部契约复制进每个 Skill。

当前 `lib/tools/createdsession.tool.yaml` 可以解析传统 Skill 声明的 12 个 Capability。MAS Skill 声明的 16 个 `ca.pdu_session.*` Capability 仍未解析；不要把设计稿中的 Tool Contract 冒充为已批准的 ToolCatalog。

## 9. Compiler 与验证状态

旧版 `ca-skill-toolchain` 仍是符合现有 v1alpha1 Schema 的旧包的机器语法权威，但它当前不支持传统 PDU Session 源码使用的节点级 `preconditions/postconditions`。

无状态 `ca-skill-compiler` v0 设计已确认，但实现尚未开始。在新 Compiler 支持当前源码结构和 Library 链接之前，当前 5GC 源码只能报告为**源码已存在 / Compiler-Link 验证 NOT_RUN 或 BLOCKED**。禁止为了制造 PASS 而静默删除、降级或改写不支持的语义。

现有命令：

```bash
make verify
python3 -B scripts/verify.py --compile skills/<name>
```

它们仍委托旧版 Toolchain。旧包通过这些命令，不代表新的 5GC 源码已经编译。未来 Compiler 构建通过也不等于 Runtime 资格验证或真实 5GC 验收通过。
