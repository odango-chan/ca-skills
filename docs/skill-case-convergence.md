# Skill / Case convergence（进行中）

本阶段接续 PR5，不修改 `connectionagent-pr5-final-composition` 冻结基线。
单文件 Case 已迁移到工作树，尚未完成最终资格验证，不代表新 composition 已可晋级。

## 2026-09-07 检查基线

已 fetch 各仓 origin/main：Skills `92cdcf4`、Platform `976b9e4`、Runtime
`2c0e03b`、governance `e83955e`、Benchmark `f013552`、Sandbox `6c5a8cc`。
Benchmark assets origin/main 是 `b41d3ea`，本地已有 `83d8763` 提交；保留已有工作。

| 包目录 | 角色 | 原 cases | 原 examples | 准入状态 |
| --- | --- | --- | --- | --- |
| 5gc-intent | routing-only，无 assurance | 无 | 有 | 不属于 executable SQ |
| ue-registration | executable | 有 | 仅占位 README | 已列入官方准入集合，本阶段待重跑 |
| ensure-session-qos | executable | 有 | 无 | 已列入官方准入集合，本阶段待重跑 |
| download-object-by-deadline | executable | 有 | 无 | 已列入官方准入集合，本阶段待重跑 |
| query-weather-for-ue | executable | 有 | 无 | 已列入官方准入集合，本阶段待重跑 |
| 5gc-file-transfer | executable migration target | 无 | 有 | 尚未资格验证 |
| wifi-file-transfer | executable migration target | 无 | 有 | 尚未资格验证 |

## examples 逐项分类

以下 B 类材料移到各自 `references/samples/`，保留相对子目录和内容：

- 5gc-intent：`01-file-transfer-routing/request.yaml`、`candidate.yaml`、`fixtures/demo-roster.yaml`：路由输入/结果和身份演示，无 Qualification contract。
- 5gc-file-transfer：`01-urgent-two-receivers/request.yaml`、`resolve-member-endpoints-output.yaml`、`02-release/request.yaml`、`fixtures/demo-endpoints.yaml`：业务输入和 Provider 输出说明，无期望路径、Case class 或资格执行入口。
- wifi-file-transfer：`01-urgent-everyone/request.yaml`：业务请求说明，无执行断言。

C 类：删除 ue-registration 的 `examples/README.md`；它只说明目前没有示例，未携带测试意图。
没有发现 A 类执行资产。跨 Platform/Runtime/Sandbox/Benchmark/assets/governance 检索未发现这些样本路径的执行消费者。
这些说明性材料不计入 Case coverage。`make verify-package-layout` 禁止所有官方包重新引入根级 `examples/`。

## 后续必须完成

- 从 Platform compiler/domain、Planning、mock fixture runner、SQ2 EvaluationScenario 和 Benchmark/Sandbox 实际消费者收敛单文件 Case schema；删除旧多文件读取路径。
- 更新官方 Cases、compiler fixtures、生成资产、authoring/review 工具和验证脚本。
- 单独核对 file-transfer 的 Capability、Predicate、Script、Provider 和 SQ 依赖；语法通过不能作为生产资格。
- 执行 compile、SQ1、SQ2、仓库完整 Gate，再进行新 composition 的不可变 pin 与治理文档晋级。

## 单文件 Case 实施进展

已将官方 Skills、本仓 Platform 回归包和 compiler fixtures 共 110 个 Case 合并。
原 metadata/classes/purpose、Context、Expected、actions、predicates、EvaluationScenario 的解析值与迁移前 Git 提交逐项相等：`CASE_SEMANTIC_PARITY_OK 110`。
新字段与消费者合同见 Platform `docs/skill-case-authoring.md`。

Platform compiler、Planning、mock fixture runner、Service Case 展示和场景事件直接读取 typed Case；不再生成或读取旧独立文件。旧路径由 `CASE_LAYOUT_DEPRECATED` 拒绝，未知字段/缺失 context 由 Schema 拒绝，examples 由 `PACKAGE_LAYOUT_INVALID` 拒绝。迁移保留了 fixture 回归和 simulation 输入的隔离。

删除 Python `test_reference_skill_cases.py` 中重复的 Procedure interpreter/coverage engine；Go Compiler/Planning/mock regression 继续验证对应语义，shared Runtime 保持正式执行权限。authoring/review 工作流已改为当前 Procedure/Predicate 和单文件 Case。

当前工作树验证：

- Compiler（显式官方 Skills root）PASS，包含四个官方 Skill compile、全部官方 Procedure syntax 检查和新的 Case 正反 Schema/目录检查。
- Planning PASS；仓内 Mock regression PASS；Service PASS；API PASS。
- qualificationruntime（显式官方 Skills root）PASS；该包结果不自动代表所有官方 Case 的 SQ2 执行。
- Python contracts 85 tests PASS。
- Skills package layout 与两个仓库 diff check PASS。

尚待处理：显式官方 Skills root 的历史 `TestMigrated*TargetMockQualification` 中 weather/download 出现 ACTION_INPUT_SCHEMA_MISMATCH；不能用仓内 mock PASS 覆盖这一结果。应核对迁移前基线与正式 sessionrun/Q4 路径，不能扩展旧 interpreter 去承接 vNext。
完整 make verify、file-transfer Registry/Case/Script 补齐、源端验证脚本的旧 Procedure 假设清理、架构/运行文档旧路径全面收敛和新 composition promotion 均未完成。
