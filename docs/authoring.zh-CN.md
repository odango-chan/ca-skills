# ConnectionAgent Skill 编写指南

本指南遵循当前语言权威文档：[Skill Language Specification](skill-language-spec.zh-CN.md)、[Script 契约](script-contract.md)、[Schema 所有权](schema-ownership.md) 和 [Authoring Model](authoring-model.md)。

**ca-skills 是官方 Skill 源码和 Skill 自有语言语义的唯一输入权威。**

## 1. 当前正式源码基线

当前正式 5GC 可执行 Skill：

- `skills/establish-pdu-session/`：传统初始 PDU Session Establishment。
- `skills/establish-pdu-session-mas/`：MAS policy-first 候选流程。

这两个包是当前语法和业务源码样例。仓库中的其他历史 Skill 暂时保留，但不再作为当前 5GC 语言契约的权威样例。

最新 `ca-agent-demo` 源码只用于核对和刷新业务行为。Compiler 与 Studio 消费本仓库的正式 Skill 源码，不直接把 ca-agent-demo 当作第二个 Skill 输入源。

## 2. 标准 Skill 目录

~~~text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/<case>/case.yaml
├── references/       # 可选模型知识
├── schemas/          # 仅 Skill 自有 Schema
└── scripts/          # 可选纯本地计算
~~~

- `SKILL.md`：面向模型的业务指导。
- `assurance/`：确定性源码契约。
- `cases/`：源码级语义义务，不是 Compiler 可执行测试。
- `references/`：可选知识，不会自动加载；在 `SKILL.md` 列出准确路径，由模型按需决定是否读取。
- `schemas/`：只放真正由 Skill 拥有的 Schema，例如公共 Request Schema。
- `scripts/`：Skill 自有的确定性本地计算。

不要创建 `preload/` 或 `on-demand/` 目录，也不要再维护一份与 Procedure 边完全重复的文字流程。

## 3. Procedure

当前语言使用命名 Procedure 和命名 Node。主节点只支持：

- `call`：一个精确的导入 Tool Operation。
- `script`：一个 Skill 自有 Script 路径。
- `procedure`：本地或显式指定跨 Skill 的 Procedure。
- `verify`：一个 Predicate。
- `reconcile`：调和原始 Mutation Node。
- `terminal`：声明的 Procedure 终态。

`call` 始终是标量 Operation ID：

~~~yaml
call: sbi.udm.sm_data.get
~~~

不要在 `call` 中填写 Capability 分组、Dependency 名称、MCP Tool 名称或 `{dependency, operation}` 对象。调用方把 ToolCatalog 字节装配到逻辑 `lib/tools/**`，Compiler 根据精确 Operation ID 链接。

Preconditions/Postconditions 是有序阶段，Step 只支持 `call`、`script` 和 `verify`，不支持嵌套 Procedure 或 Tool 声明。

必须显式使用 `with:` 绑定。每个绑定只能有 `from:` 或 `value:`。不要依赖隐式前序节点输出或自动推断数据流。

## 4. Scripts

统一使用唯一入口：

~~~python
from typing import Literal, TypedDict

class SelectionOutput(TypedDict):
    accepted: Literal[True]
    dnn: str

def main(input: dict) -> SelectionOutput:
    return {"accepted": True, "dnn": input["dnn"]}
~~~

- `input: dict` 只是调用容器，不是开放的 Input Schema。
- Procedure Script 输入按调用点的 `with:` Producer 绑定派生。
- Predicate Script 输入由 Host 创建的 Predicate Evaluation Context 和声明的 Observation 组成。
- 返回类型必须是非空、静态声明的 `TypedDict`。
- Compiler 自动生成只读 Script Output JSON Schema。
- JSON wire key 不是合法 Python 标识符时，使用函数式 `TypedDict("Name", {...})`，例如 `5qi`。
- 不要再添加 `# /// connectionagent-tool` 元数据、独立 local Tool ID 或 Script 输入/输出 Schema 文件。
- Script 只做确定性本地计算，不调用 HTTP、MCP、Provider、Tool、Shell、数据库、时钟或随机源。

精确支持类型和约束见 [Script Contract](script-contract.md)。

## 5. Schema 所有权与外部导入

| 契约 | Owner | 来源 |
|---|---|---|
| Skill 公共 Request | Skill | `schemas/**` |
| Tool Operation Input/Output | Tool Owner | 逻辑 `lib/tools/**` 下的导入 ToolCatalog |
| Subject / Facts / Evidence | Agent Host | 逻辑 `lib/host/**` 下的显式 Owner Schema 引用 |
| Observation Payload | Observation Owner | 逻辑 `lib/observations/**` 下的显式 Owner Schema 引用 |
| Procedure Script 输入 | 派生 | 精确调用点 Producer 绑定 |
| Predicate Script 输入 | Host + Observation Owner | Predicate Evaluation Context |
| Script 输出 | Skill Script | 从 Output `TypedDict` 自动生成 |

`requiredFacts` 是事实标识符列表，不是字段级 Schema。不要伪造外部 Schema，不要从 Python 访问模式推断，也不要用 Deployment Profile 替代。

当前正式 `lib/` 快照只包含传统 PDU 的 12-Operation ToolCatalog。真实 Host Subject/Facts/Evidence 和 Observation Owner Schema 尚未随仓库提供；这是明确的外部依赖，使用到时 Compiler 必须报告缺失。

MAS Skill 的 16 个 Operation 引用仍未解析，直到 Tool Owner 提供正式批准的 ToolCatalog。设计文件不能作为正式导入契约。

## 6. Cases 与验证

一个 Case 对应一个 `cases/<name>/case.yaml`，记录源码级场景和预期语义义务。它不代表已经执行、通过 Qualification 或完成真实 5GC 验收。

运行：

~~~sh
make verify
~~~

它只检查仓库本地源码卫生、Script 入口形状、源码引用和语义 Token 注册表，不调用 Compiler、Runtime、Qualification 或真实网络。

Compiler 验收必须使用实际目标 Compiler；Runtime 和真实 5GC 验收由各自 Owner 负责。

## 7. Compiler 与 Studio 边界

Studio/调用方负责获取文件、导入 Tool/Host/Observation 契约，并组装逻辑 BuildRequest 文件集合。Compiler 接收字节，解析和链接 Skill 语言、校验绑定、生成产物和诊断。

Compiler 不管理 Git、Upload、MCP、依赖、Lock、Cache、工作区目录、Python 执行、Tool 执行或 Qualification。Studio 决定如何展示和导出 BuildResult。
