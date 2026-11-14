# ConnectionAgent Skill Language Specification

**Canonical specification:** [ConnectionAgent Skill Language Specification（CA-SL）— 中文完整规范](skill-language-spec.zh-CN.md)

The linked document is the sole normative CA-SL v1alpha3 specification for this repository (`vNext` is a non-normative series alias). It includes the language background, conceptual model, terminology, YAML grammar, static and runtime semantics, ToolCatalog / CapabilityContracts, Observation and Evidence model, error handling, PDU Session examples, toolchain requirements, design references, decision register and review FAQ.

The [first v1alpha3 errata record](design/ca-sl-v1alpha3-errata-2026-11-14.md), [second errata review](design/ca-sl-v1alpha3-errata-2026-11-14-r2.md), [diagnostic/PSI trace errata](design/ca-sl-v1alpha3-diagnostic-trace-errata.md), [interop/implementation baseline clarification](design/ca-sl-v1alpha3-interop-clarifications-2026-11-14.md), [Reconcile/Runtime diagnostic errata](design/ca-sl-v1alpha3-reconcile-runtime-errata-2026-11-14.md), [Evidence/source/routing/schema errata](design/ca-sl-v1alpha3-evidence-source-and-routing-errata.md) and [editorial review closure](design/ca-sl-v1alpha3-editorial-closure-2026-11-14.md) and [interop audit / conformance routing clarification](design/ca-sl-v1alpha3-interop-audit-2026-11-14.md) and [receipt anchor audit](design/ca-sl-v1alpha3-receipt-anchor-audit-2026-11-15.md) and [excerpt review / routing scope clarification](design/ca-sl-v1alpha3-excerpt-review-scope-2026-11-15.md) track documentary clarifications and incomplete executable fixtures. None independently changes the frozen language target.

This English-path document is an index only. It intentionally does not duplicate the normative language definition. Until an approved English translation is published, the Chinese document remains the sole authoritative v1alpha3 language contract. The source language and its normative Appendices F/G/H are frozen; the complete Root Routing / Applicability author syntax is not defined by v1alpha3, although ambiguous Skill selection must fail closed.  Owner, Compiler, Studio, Runtime and 5GC implementation conformance are separately gated by §45.2.

**Version:** `connectionagent.io/v1alpha3` (vNext is an informative alias)  
**Status:** FROZEN LANGUAGE + INTEROPERABILITY CONTRACT — IMPLEMENTATION NOT QUALIFIED  
**Owner:** ca-skills
