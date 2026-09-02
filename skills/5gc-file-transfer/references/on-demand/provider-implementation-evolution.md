# Provider Implementation Evolution

This Skill depends on stable Capability semantics. It does not depend on how a deployment currently implements those semantics.

The reference Capability is:

```text
transfer.participants.resolve_endpoints
```

Its canonical contract stays stable:

```text
input
  senderImsi
  receiverImsis

output
  members[]
    imsi
    ip
```

The Provider implementation may evolve without changing `SKILL.md`, `assurance/procedure.yaml`, or the Capability semantic ID.

## P0: fixture-backed Provider

For the current deterministic demo, endpoint state is declared in:

```text
examples/fixtures/demo-endpoints.yaml
```

A fixture-backed Provider performs a bounded lookup by IMSI and returns the canonical Capability result.

The fixture is runtime Provider state. It is deliberately separate from the `core5g-intent` identity roster.

```text
identity roster
  Leo -> IMSI

endpoint fixture
  IMSI -> current demo IP
```

Do not merge these two fixtures just because the current demo values are static.

## Next: stateful mock Provider

When tests need endpoint changes, missing sessions, stale state, or controlled failures, the same Capability can bind to a stateful mock Provider.

Examples:

```text
IMSI has no active endpoint
IP changes after session recreation
provider returns UNKNOWN
one participant resolves and another does not
```

The Provider must still return either one complete canonical bounded member set or a non-success outcome. It must not return an incomplete list that silently omits participants.

## Later: governed script Provider

A deployment may implement the Capability with a script that calls one or more concrete read/query Tools:

```text
transfer.participants.resolve_endpoints
  -> ProviderBinding
  -> governed Provider script
  -> allowed read/query Tools
  -> normalize concrete results
  -> canonical members[]
```

The script belongs to the Provider/deployment implementation layer, not to the Skill-local `scripts/` directory.

Provider scripts may perform external reads only through explicitly authorized dependencies. They do not inherit arbitrary Tool access from the Agent or Skill.

A ProviderBinding/Provider artifact should freeze at least:

```text
capability semantic ID + version
implementation identity/version
allowed concrete Tool dependencies
timeout/budget policy
input/output normalization contract
implementation digest
```

For a `read_only` Capability, the implementation must not expand authority into mutation Tools.

## Production: native Provider

A production deployment may replace the script with direct integration against SMF state, Service Fabric state, an SBI adapter, or another certified source:

```text
transfer.participants.resolve_endpoints
  -> Free5GC Provider

transfer.participants.resolve_endpoints
  -> Open5GS Provider
```

The Skill remains unchanged as long as every Provider satisfies the same frozen Capability contract and qualification requirements.

## Provider script vs Predicate script

These are different execution surfaces.

### Skill-local Predicate evaluator

```text
assurance/predicates.yaml
  -> CEL or Skill-local Python evaluator
```

A Predicate script is deterministic local judgement only:

```text
effect: local_compute
network: denied
no Tool/Capability dispatch
```

### Provider implementation script

```text
Capability
  -> ProviderBinding
  -> Provider script
```

A Provider script may perform governed external reads/calls required to implement the Capability, but only through the exact dependencies authorized by the Provider/deployment contract.

Do not place a Provider implementation script under Skill-local `scripts/` merely because both happen to use Python.

## Design rule

The stable dependency is:

```text
Skill / Procedure
  -> Capability semantic contract
```

The replaceable implementation is:

```text
ProviderBinding
  -> fixture
  -> stateful mock
  -> governed script + Tool
  -> native Provider
```

Static data should remain declarative while it is static. Introduce code only when the Provider needs behavior.
