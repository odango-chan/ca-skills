# Repository documentation / 仓库文档

## Language / 语言

- [CA-SL specification](skill-language-spec.md) · 当前规范和历史版本入口
- [v1alpha5 release record](releases/ca-sl-v1alpha5.md) · 规范、配套契约与勘误
- [IngressCatalog v1alpha1](design/integration-ingress-operation-contract-vnext.zh-CN.md) · 入站事件与配对响应契约
- [Ingress diagnostics](design/ingress-diagnostic-registry-v1alpha1.md) · 诊断注册表及 [JSON](design/ingress-diagnostic-registry-v1alpha1.json)
- [Schema Closure Digest v1](design/schema-closure-digest-v1.md) · Ingress Schema 摘要算法
- [Specification editorial guidelines](design/ca-sl-editorial-guidelines.md) · 规范编辑准则

## Authoring / 编写

- Authoring guide · [English](authoring.md) / [中文](authoring.zh-CN.md)
- Package structure · [Layout](project-layout.md), [authoring model](authoring-model.md) and [Schema ownership](schema-ownership.md)
- [v1alpha5 PDU Session examples](../examples/README.md) · 传统 5GC 和 OpenAMSM MAS
- [MAS Modify / Release source mapping](mas-lifecycle-source-mapping.md) · pinned OES steps, callable identities and candidate Schemas
- [MAS Modify / Release Owner contract](mas-lifecycle-owner-contract.md) · mutation outcomes, receipts, Evidence and Scope
- [MAS Modify / Release acceptance matrix](mas-lifecycle-acceptance-matrix.md) · static regression coverage and unrun runtime cases

## Repository layout / 目录

| Path | Contents |
| --- | --- |
| [`examples/`](../examples/README.md) | Current-language authoring examples |
| [`skills/`](../skills/README.md) | Historical source packages used as behavior fixtures |
| [`lib/`](../lib/README.md) | Imported legacy ToolCatalog snapshot |
| [`language/`](../language/README.md) and [`spec/`](../spec) | Historical semantic-token registries |
| [`scripts/`](../scripts) and [`tests/`](../tests) | Source and document verification |
| [`artifacts/acceptance/`](../artifacts/acceptance) | Dated acceptance records and their harnesses |

## Historical material / 历史资料

- [Design and review archive](archive/README.md) · 早期设计、评审和迁移材料
- [Legacy 5GC source baseline](current-5gc-skill-baseline.md) and [integration notes](skills/establish-pdu-session-integration.md)
- [Legacy Python Script contract](script-contract.md)
- File-transfer behavior contracts · [Business resource identity](business-resource-identity.md) and [network policy identity](network-policy-identity.md)
