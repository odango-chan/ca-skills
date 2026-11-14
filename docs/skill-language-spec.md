# ConnectionAgent Skill Language Specification

**Canonical specification:** [ConnectionAgent Skill Language Specification（CA-SL）— 中文完整规范](skill-language-spec.zh-CN.md)

The linked document is the sole normative CA-SL vNext specification for this repository. It includes the language background, conceptual model, terminology, YAML grammar, static and runtime semantics, ToolCatalog / CapabilityContracts, Observation and Evidence model, error handling, PDU Session examples, toolchain requirements, design references, decision register and review FAQ.

The [first v1alpha3 errata record](design/ca-sl-v1alpha3-errata-2026-11-14.md), [second errata review](design/ca-sl-v1alpha3-errata-2026-11-14-r2.md) and [diagnostic/PSI trace errata](design/ca-sl-v1alpha3-diagnostic-trace-errata.md) track documentary clarifications and incomplete executable fixtures. None independently changes the frozen language target.

This English-path document is an index only. It intentionally does not duplicate the normative language definition. Until an approved English translation is published, the Chinese document remains the sole authoritative v1alpha3 language contract. The source language and its normative Appendices F/G/H are frozen; Owner, Compiler, Studio, Runtime and 5GC implementation conformance are separately gated by §45.2.

**Version:** vNext / API v1alpha3  
**Status:** FROZEN LANGUAGE + INTEROPERABILITY CONTRACT — IMPLEMENTATION NOT QUALIFIED  
**Owner:** ca-skills
