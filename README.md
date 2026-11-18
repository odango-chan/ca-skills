![ConnectionAgent Skills](assets/repo-banner.svg)

# ConnectionAgent Skills

[简体中文](README.zh-CN.md)

Official source for ConnectionAgent Skills and the CA-SL language specification. **CA-SL v1alpha5 is frozen.** Use the [release record](docs/releases/ca-sl-v1alpha5.md) to pin the specification and its companion Ingress contract.

| Start here | Contents |
| --- | --- |
| [Specification](docs/skill-language-spec.md) | Current CA-SL target, companion contracts and previous releases |
| [Authoring guide](docs/authoring.md) | Skill package layout, Procedure, Predicates, Schemas and Scripts |
| [PDU Session examples](examples/README.md) | v1alpha5 source examples for conventional 5GC and OpenAMSM MAS |
| [Repository documentation](docs/README.md) | Authoring references, historical baselines and design archive |

The examples require trusted Owner contracts and remain `NOT_QUALIFIED`. The [historical Skill packages](skills/README.md) and [imported snapshots](lib/README.md) retain their original paths for existing consumers.

Run `make verify` for source hygiene, specification structure and Wait/Ingress registry checks. Compiler, Runtime and live 5GC qualification use separate acceptance tests.
