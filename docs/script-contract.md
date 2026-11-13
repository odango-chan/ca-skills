# Skill-owned Python Script Contract — Companion Specification

**Status:** Detailed companion contract. The [CA-SL vNext Specification](skill-language-spec.zh-CN.md) is the sole normative language authority. If any wording here conflicts with it, the CA-SL specification takes precedence.

This document may retain implementation-level detail for supported Python annotations, TypedDict output derivation and static restrictions. It must not introduce a second Script input schema, separate Tool identity, or semantics that differ from CA-SL.

Core rules:
- The only entry point is main(input: dict) -> OutputTypedDict.
- Procedure Script input derives from its explicit call-site with bindings.
- Predicate Script input derives from its owning Predicate parameters signature.
- Host / Runtime attaches reserved Evidence refs; Script cannot create or widen them.
- Compiler generates Output Schema from the return TypedDict and does not execute Python.
- Scripts are deterministic local computation only and cannot call external systems.
