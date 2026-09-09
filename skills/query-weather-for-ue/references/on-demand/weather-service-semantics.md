# Weather service semantics

The Weather Tool is an external business Tool, not a 3GPP core-network capability.

This Skill depends on the stable semantic capability `external.weather.query`. A deployment may bind that capability to different operator or test Weather MCP Tools without changing the Skill.

The canonical input includes at least:

- `city`
- `unit`

This reference package uses `celsius`.

A successful raw result must contain a non-empty `city`, a finite numeric `temperature`, and a non-empty `condition`. Local normalization may trim whitespace and normalize numeric representation only. Missing fields, empty strings, or non-finite temperatures are explicit failures; the normalizer must not invent `unknown`, `0.0`, or other fallback values.

A hard precondition for invocation is:

```text
user_plane.connectivity.available = PASS
```

A Tool may be discoverable while this precondition is unsatisfied. In that case the planning context may still expose the resource, but it must be treated as `invocable=false`; discovery does not authorize direct invocation.

`external.weather.query=SUCCEEDED` means only that the external call completed. It does not establish Skill success. After normalization, `verify-weather-result` independently evaluates `service.weather.query.succeeded`; only `PASS` may reach the `SUCCEEDED` terminal.
