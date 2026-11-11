# Current Skill Authoring Model

**Status:** current source-authoring guidance; compiler acceptance is pending. This document records the authoring semantics used by the two current 5GC Skills. It is not a substitute for a machine schema.

## 1. One deterministic source graph

- `assurance/procedure.yaml` is the deterministic workflow source.
- `SKILL.md` is model-facing business guidance for an LLM-driven path.
- Do not manually maintain a second prose graph with duplicated next-node edges.
- Both execution styles must retain the same admitted capabilities, Predicate truth, evidence authority and final Contract boundary.

## 2. Business-significant nodes

A main Procedure node should represent a business-significant operation, side-effect boundary, independent asynchronous procedure, recovery boundary, or recognizable protocol/service step.

Do not create main-flow nodes merely for a local projection, deterministic calculation, read-only context preparation, or a single fact check when these can be expressed as preparation owned by the consuming node.

## 3. Node preconditions

`preconditions` are an ordered node-entry phase. They complete immediately before the node's main operation.

They may contain ordered, side-effect-free preparation such as:

- governed local `script` computation;
- read-only Capability calls;
- `verify` of current facts;
- a read-only child Procedure that waits for convergence.

They must not contain mutations, hidden resource creation, or operations requiring mutation reconciliation. The block stops at the first non-successful step. Its aggregate route distinguishes a proven failure from unresolved evidence.

Node preconditions do not replace Runtime/Harness hard guards. The Runtime must still recheck attempt, lifecycle, authority and mutation admission immediately before dispatch; do not copy those implementation guards into every Skill node.

## 4. Node postconditions

`postconditions` establish facts after the node's main operation and before the business flow may advance.

- Successful read/local-compute results and committed mutations enter the postcondition phase when one is declared.
- Steps are ordered; the block stops at the first non-PASS result.
- Only the block's PASS route advances after every step passes.
- FAIL and UNKNOWN follow the block's explicit routes.
- A mutation being COMMITTED does not by itself establish the business fact.

Node-level postconditions are not the same as `SkillContract.spec.postconditions`. The former govern whether one operation may advance; the latter remain the independent final acceptance conditions for the whole Skill.

## 5. Shared preparation results

A preparation result belongs inside a node when only that node consumes it. When later business nodes also consume it, it is shared Procedure data. Current source names the producer through paths such as:

```yaml
from: <producer-node>.preconditions.<step-name>.output
```

Do not copy values into new inputs or invent implicit previous-node bindings. The compiler must resolve the exact producer path or report it unresolved.

## 6. Reconciliation

Use native `reconcile: <original-node>` for reconciliation of an original mutation. Do not model a second generic Tool call as an unrelated reconcile operation. Preserve the original operation identity and its uncertainty; never blindly retry an unknown mutation.

## 7. Cases are obligations, not execution evidence

A Case records a scenario, context and expected outcome. It does not prove that a compiler, mock runtime, qualification suite or live network executed it. Keep source coverage and executed acceptance evidence separate.

## 8. Compiler compatibility

The current `ca-skill-toolchain` `procedure-source.schema.yaml` does not define node-level `preconditions/postconditions`. The accepted stateless Compiler v0 design is tracked by [ca-skill-toolchain#133](https://github.com/odango-chan/ca-skill-toolchain/issues/133); the new `ca-skill-compiler` repository is bootstrap-only and implementation is NOT_STARTED.

Until the new compiler supports these source semantics and imported Library resolution, report compile/link validation as NOT_RUN/BLOCKED. Never flatten or drop the source semantics to satisfy the legacy schema.
