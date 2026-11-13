# ConnectionAgent Skill 编写指南

**规范权威：** [ConnectionAgent Skill Language Specification（CA-SL）](skill-language-spec.zh-CN.md)

本文件不单独定义语言语法。所有术语、YAML 语法、绑定、Tool / Observation / Capability、Schema、Evidence、异常和使用示例均以 CA-SL 综合规范为准。

当前仓库中的传统 5GC Skill 仍是 v0.2 业务行为基线，尚未完成 vNext 迁移。MAS 是设计候选，不是第一阶段真实执行验收基线。

vNext 推荐源码目录：

~~~text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
├── schemas/
├── scripts/
└── references/
~~~

vNext 不要求作者维护独立的 contract.yaml 或 SkillContract YAML 对象。procedure.yaml 根字段包含 goal、requestSchema、capabilities 和唯一 Procedure 图；入口 Precondition 与最终 Postcondition 都是图中的显式节点。Compiler 生成 Runtime 所需的规范化契约和执行产物。

编写时先阅读 CA-SL 规范中的：
1. 概念模型与源码布局；
2. Procedure 四种节点、入口 / 最终门禁和控制流；
3. Predicate.parameters 与显式 arguments；
4. ToolCatalog、Capability 和 Schema 所有权；
5. Procedure Script 与 Predicate Script；
6. Observation、Evidence、Reconcile 和并发隔离；
7. PDU Session 示例和 FAQ。

本指南是导航页，不得作为独立语言规范或 Compiler 验收依据。
