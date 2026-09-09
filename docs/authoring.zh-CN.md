# ConnectionAgent Skill 编写指南

本文档面向需要新增或修改官方 Skill 的开发者，说明 `connectionagent-skills` 仓中的编写方式、边界和验证流程。

详细 YAML / Script 语法见：

```text
.agents/skills/create-connectionagent-skill/references/authoring-syntax.md
```

机器语法是否合法，以 `connectionagent-skill-platform` 当前的 Schema 和 Compiler 为准。

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

### 路由策略 / Model Context 包

如果内容只是给 Agent 提供业务语义、归一化规则或路由策略，本身并不需要交给 Runtime 执行 Procedure，则使用 model-context 形式。

`5gc-intent` 是当前参考。

路由属于 Agent 自身行为，不要设计成“先执行一个 routing Skill，再由它返回另一个 Skill 的执行目标”。

### Runtime Capability

底层 Provider 动作，例如查询、创建、修改、删除，一般属于 Runtime Capability，不需要为了单个底层动作再包装一层 Skill。

如果不确定边界，可参考：

```text
.agents/skills/create-connectionagent-skill/references/skill-granularity.md
```

## 2. 标准目录结构

仅提供 Model Context 的包可以很简单：

```text
skills/<name>/
├── SKILL.md
├── references/    # 可选
└── schemas/       # 可选
```

可执行 Skill 的标准结构为：

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
- 每个 Qualification Case 只使用一个 `cases/<case>/case.yaml`；
- Skill 根目录不使用 `README.md`、`MIGRATION.md`、`examples/`；
- 说明性示例放在 `references/samples/`；
- `skills/` 下给模型看的 Markdown 统一使用英文；
- 不创建空目录占位。

## 3. `SKILL.md` 写什么

`SKILL.md` 是 Skill 根目录中给模型看的入口文件，应尽量薄，只保留会影响模型决策的内容：

- 什么情况下使用这个 Skill；
- 对应的业务或领域目标；
- 输入如何归一化、如何消歧；
- 模型需要理解的输入输出语义；
- 哪些信息不能猜、哪些边界不能绕过。

不应放进 `SKILL.md` 的内容包括：

- Provider 实现和映射；
- 部署地址、凭据；
- ObservationBinding；
- Runtime 状态机；
- Qualification 状态；
- Benchmark 评分规则；
- 迁移历史；
- 大段系统架构教程。

这些内容属于各自的实现仓或工程文档，不属于模型上下文。

## 4. `assurance/` 三个文件分别负责什么

对于可执行 Skill：

| 文件 | 职责 |
| --- | --- |
| `contract.yaml` | 声明目标、允许使用的资源、前置条件、可满足要求、后置条件以及 Planning 约束 |
| `procedure.yaml` | 声明确定性的流程结构、数据绑定和结果路由 |
| `predicates.yaml` | 声明需要观察什么，以及如何基于已获取 Evidence 做确定性判断 |

对应的 Platform 权威 Schema：

| Skill Source | Platform Schema |
| --- | --- |
| `assurance/contract.yaml` | `schemas/v1alpha1/skill-contract.schema.yaml` |
| `assurance/procedure.yaml` | `schemas/v1alpha1/procedure-source.schema.yaml` |
| `assurance/predicates.yaml` | `schemas/v1alpha1/predicate-set.schema.yaml` |
| `cases/<case>/case.yaml` | `schemas/v1alpha1/skill-test-case.schema.yaml` |
| Python Script 元信息 | `schemas/v1alpha1/script-tool-metadata.schema.yaml` |

当前 `procedure.yaml` 应以 `procedure-source.schema.yaml` 为准，使用 object-form Procedure vNext：

```text
procedures
  -> <procedure>
       -> start
       -> nodes
```

不要从历史 `procedure-set.schema.yaml` 推导当前 Skill Source 写法。

详细节点、Binding、Predicate、Script 和 Case 示例统一放在：

```text
.agents/skills/create-connectionagent-skill/references/authoring-syntax.md
```

## 5. Observation、Evidence 与 Predicate

这三者不要混在一起理解。

Runtime 先根据 Predicate 声明获取所需 Observation，并形成可供判断的 Evidence。随后 Evidence Gate 检查所需数据是否存在、是否新鲜、是否可用。

如果必要 Evidence 缺失、过期或不可用，应得到 `UNKNOWN`，而不是把“没有证据”误判成业务 `FAIL`。

Evaluator 的建议：

- 简单、可审计的确定性判断优先使用 CEL；
- 复杂但仍然确定性的领域判断使用 governed Predicate Script。

Predicate Script 只能判断已经提供的数据，不能主动调用 Provider、MCP、网络服务，也不能自行重新获取 Evidence。

## 6. Qualification Case 怎么写

Skill Case 是 Skill Source 的 Qualification 资产，不是 Benchmark Case。

每个 Case 一个文件：

```text
cases/<case>/case.yaml
```

Case 数量不需要固定，应覆盖该 Skill 真正存在的语义义务。常见覆盖包括：

- 正常成功；
- 操作失败或被拒绝；
- Evidence `UNKNOWN`；
- mutation 的 `OUTCOME_UNKNOWN` 以及后续 reconcile；
- Planning / Budget 限制；
- 后置条件独立验证失败。

不要把 mock / fixture 返回值直接当成业务成功证明。最终结果仍应由后置条件或独立 Evidence 证明。

SkillTestCase 也不能替代 BenchmarkCase。Benchmark 的黑盒裁决不能直接依赖 Skill 内部预期路径。

## 7. 优先参考真实 Skill，不再维护第二套教学例子

新增 Skill 时，优先找最接近的正式包参考：

| 需求 | 参考 Skill |
| --- | --- |
| 完整但较紧凑的端到端流程 | `query-weather-for-ue` |
| mutation / `OUTCOME_UNKNOWN` / reconcile | `ue-registration` |
| requirements 与 postconditions | `ensure-session-qos` |
| deadline 与本地计算 | `download-object-by-deadline` |
| 非执行型路由策略 | `5gc-intent` |

真实 Skill 会跟随 Compiler 持续验证，比额外维护一套教学包更可靠。

## 8. 推荐编写流程

新增或结构性修改 Skill 时，按下面顺序进行：

1. 阅读仓库根目录 `AGENTS.md`。
2. 判断这是可执行 Skill、routing/model-context，还是 Runtime Capability。
3. 找 1～2 个最接近的正式 Skill 参考。
4. 优先复用已有 Registry 中的 Capability、Predicate 和 Schema。
5. 需要改 `assurance/`、Script 或 Case 时，按需查看 `references/authoring-syntax.md` 对应章节。
6. 单独编译当前 Skill：

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

   如果 `connectionagent-skill-platform` 不在兄弟目录 `../connectionagent-skill-platform`，设置：

   ```bash
   export CONNECTIONAGENT_SKILL_PLATFORM_ROOT=/path/to/connectionagent-skill-platform
   ```

7. 提交前运行完整仓库验证：

   ```bash
   make verify
   ```

8. 如目标是更高等级 Qualification 或生产环境准入，再进入 Platform / Runtime / Sandbox 对应流程。

编译通过或本地 preflight 通过，不等于 production-qualified。

## 9. 仓库之间的边界

可以简单记成：

```text
connectionagent-skills
  怎么写 + 官方 Skill Source

connectionagent-skill-platform
  Schema + Compiler + Qualification

connectionagent-runtime
  Admission + Binding + Deterministic Execution
```

当某个真实场景暂时表达不出来时，不要首先扩展 Skill 语法。先确认缺口究竟来自：

- ProviderBinding；
- ObservationBinding；
- Runtime 能力；
- Qualification；
- Sandbox / 集成环境。

只有确认现有语言本身确实无法表达必要语义时，才考虑修改 Skill Language。
