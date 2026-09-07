# Skill / Case convergence（进行中）

本阶段接续 PR5，不修改 `connectionagent-pr5-final-composition` 冻结基线。
尚未完成 Case consumer 迁移或最终资格验证，不代表新 composition 已可晋级。

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
