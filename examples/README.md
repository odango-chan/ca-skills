# CA-SL example packages

The two authoring examples use the *frozen CA-SL v1alpha4 syntax* and live at `examples/skills/<name>`. At build time the logical Skill package root is still **`skills/<name>`** as required by CA-SL G.7; `examples/` is a repository packaging folder, not a change to the Compiler's logical package identity.

- `examples/skills/establish-pdu-session` — conventional Open5GS / UE-requested PDU establishment.
- `examples/skills/establish-pdu-session-mas` — SMF MAS policy-first design.

`examples/legacy/` preserves the full pre-migration source, scripts, and 36+6 Case files as **historical behavioral baselines only**. Do not feed those v1alpha1/v0.2 files into a v1alpha4 Compiler or claim legacy Case tests pass.

**Qualification:** The source files under `examples/skills/` show correct v1alpha4 author *shape*, but have explicitly illustrative (`urn:example:`) Owner/Host dependency aliases, Schema IDs, Capability names and expected outputs. Those are NOT signed/published v1alpha4 Owner contracts. Correct Compiler behavior in this repository is an explicit link/identity failure, not guessed exports or auto-generated v1alpha4 snapshots. Both examples remain NOT_QUALIFIED and MUST NOT be deployed. Compare legacy for business parity, and migrate every old case into actual v1alpha4 Fixture only when real Owner schemas are available.

**Frozen source of truth:** [CA-SL v1alpha4 at `7f84393`](https://github.com/odango-chan/ca-skills/blob/7f84393ee8c395e4d8c39a74cb5000a1f896588d/docs/skill-language-spec.v1alpha4.zh-CN.md). Compiler BuildRequest must select `connectionagent.io/v1alpha4`, ToolCatalog must be `connectionagent.io/toolcatalog/v1alpha4`, CapabilityContracts must be `connectionagent.io/capability-contracts/v1alpha4`, with trusted full snapshot identity and no v1alpha3 fallback.
