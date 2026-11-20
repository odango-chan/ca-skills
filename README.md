# ConnectionAgent Skills

[简体中文](README.zh-CN.md)

ConnectionAgent Skill Language (CA-SL) describes how a Skill declares its inputs, calls tools, and verifies that it reached its goal. This repository publishes the language specification, authoring guides, and Skill examples.

## Current release

**CA-SL v1alpha5** (`connectionagent.io/v1alpha5`) is the current frozen language. The [release record](docs/releases/ca-sl-v1alpha5.md) links to the exact specification and companion IngressCatalog contract, and records editorial corrections.

- Read the [language specification](docs/skill-language-spec.md) for syntax and semantics.
- Use the [authoring guide](docs/authoring.md) to write a Skill.
- See the [documentation index](docs/README.md) for schemas, diagnostics, and historical material.

## Examples

| Skill | What it shows |
| --- | --- |
| [Conventional 5G Core PDU Session](examples/skills/establish-pdu-session/SKILL.md) | A UE-requested session with an inbound event wait and an explicit final Postcondition. |
| [OpenAMSM MAS PDU Session](examples/skills/establish-pdu-session-mas/SKILL.md) | A policy-first session flow based on the OpenAMSM NW Agent plan. |
| [OpenAMSM MAS Modify](examples/skills/modify-pdu-session-mas/SKILL.md) | A source-aligned Modify Procedure with separate UPN mutation occurrences and Host-classified entry variants. |
| [OpenAMSM MAS Release](examples/skills/release-pdu-session-mas/SKILL.md) | A source-aligned Release Procedure with explicit trigger mapping and no automatic compensation / replan. |

The [examples](examples/README.md) illustrate v1alpha5 source. Linking and running them requires trusted Owner contracts and deployment bindings. Product qualification is tracked in the release record.

## Local verification

With Git, Make, and Python 3.11 available, run:

```sh
git clone https://github.com/odango-chan/ca-skills.git
cd ca-skills
make verify
```

This checks package layout and local references, specification structure, and the Wait and Ingress registries.

## Contributing

See the [contribution guide](CONTRIBUTING.md) for reporting issues, preparing changes, and verifying a pull request.

## License

A repository-wide license is pending. See the [source provenance and licensing notes](docs/source-provenance.md).
