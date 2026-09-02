---
name: download-object-by-deadline
description: 在给定截止时间前把指定对象下载完成；LLM 不猜测对象大小或低层 QoS，而是使用可信输入与可观测能力形成高层业务意图并由独立 Oracle 判定成功。
---

# Download Object by Deadline

## 目标

在给定 `deadline` 前完成目标对象向指定 UE 的下行下载，并用独立业务证据确认传输完成且没有超过截止时间。

## 使用时机

当业务目标明确包含 `ueRef`、`objectRef`、`deadline` 和 `direction=downlink`，并需要根据对象大小、可用容量和平台策略收敛所需连接/QoS 后执行下载时使用本 Skill。

## 处理原则

1. 不猜测 `sizeBytes`、DNN、S-NSSAI、5QI 或安全余量。
2. `sizeBytes` 只有在调用方提供可信值时才直接使用；否则通过只读 Metadata Capability 获取。
3. 对象大小未知且 Metadata 不可观测时，规划必须阻断或要求补充可信信息。
4. QoS 需求解析由版本化平台 Policy / Capability 完成；LLM 只表达业务目标并选择已声明能力。
5. Capacity 估算只用于判断计划是否可行，不等于下载已经完成。
6. Session 建立、QoS 配置完成或 Download Capability 返回 `COMMITTED` 都不能单独视为 Skill Goal 成功。
7. 最终成功必须同时满足 `file_transfer.completed=PASS` 和 `file_transfer.deadline_met=PASS`。
8. 具有副作用的动作返回 `OUTCOME_UNKNOWN` 时，不得直接重试，恢复由 Runtime recovery contract 处理。
9. 当前缺少可行路径所需 Capability / Tool 或可信输入时，不生成不可执行 Procedure。

## 参考资料

本 Skill 当前没有必须提供给模型的额外 Reference；执行真相由 `assurance/contract.yaml`、`assurance/procedure.yaml`、`assurance/predicates.yaml`、Tool Schema 和 Runtime policy 提供。

如果未来需要增加大对象传输策略、运营商差异或异常处理说明，应按需要分别放入 `references/preload/` 或 `references/on-demand/`，而不是扩写执行状态机到本文件。

## 简短示例

- 调用方提供可信 `sizeBytes`：直接进入容量与 QoS 需求解析，不重复查询对象元数据。
- `sizeBytes` 缺失但 Metadata Capability 可用：先只读获取大小，再继续规划。
- 下载动作已提交但截止时间证据未通过：业务目标仍然失败。
