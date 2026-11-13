# ConnectionAgent Skill 编写指南

**规范权威：** [ConnectionAgent Skill Language Specification（CA-SL）](skill-language-spec.zh-CN.md)

本文件不再单独定义一套编写语法。所有术语、YAML 语法、绑定、Tool / Observation / Capability、Schema、Evidence、异常和使用示例均以 CA-SL 综合规范为准。

当前仓库中的传统 5GC Skill 是既有业务行为参考，尚未完成 vNext 迁移。MAS 是设计候选，不是第一阶段真实执行验收基线。

推荐目录：

~~~text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
├── schemas/
├── scripts/
└── references/
~~~

编写时先阅读 CA-SL 规范中的：
1. 概念模型与术语；
2. SkillContract / Procedure / Predicate 语法；
3. Binding 和 Schema 所有权；
4. Observation 与 Evidence；
5. 异常处理、Reconcile 和并发隔离；
6. PDU Session 示例和 FAQ。

本指南是导航页，不得作为独立语言规范或 Compiler 验收依据。
