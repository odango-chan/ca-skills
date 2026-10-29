# CreatedSession Toolchain recompile at ca-skills b10a8ad

## Scope

Recompiled the current committed `ca-skills` source at `b10a8adc90342e16c918d76755c8f1a4e9bc6a01` with Toolchain PR #132 candidate `882ac439b8bd182213b06fc49be4389731269b30` and its checked-in `registry/`. This confirms the current compiler finding set against the exact source commit; it does not make the PR #132 candidate the Toolchain mainline authority.

## Results

- `5gc-file-transfer`: `VALID`, zero findings; package digest `sha256:0dbc8454ee2ee8933857664b2565b84df94245da53d53f04c0bf34b64ce621ca`.
- `establish-pdu-session`: `INVALID`, one finding, `PR5_VNEXT_RECONCILE_EFFECT_INVALID`; package digest `sha256:cecc4a252ba33cbe91ca433ba0c35882d335992c30e9aa220194a24cdc096127`.
- Both reports use schema digest `sha256:3fe530870dafe1f40f0031bfcd8118158c00dd0bcdc0ab9a9bd6d45bd99a6df2` and registry digest `sha256:961b776567719a53be81a31ae3c4f105540449299c5113fbbb5cd0fdeb00d9db`.

The child failure means the native `reconcile` owner must resolve to a registered mutation Capability. Predicate registration findings are absent. The missing mutation CapabilityContract authority is Runtime-owned; this goal treats `ca-runtime` as read-only, so no registry entry was fabricated and no Runtime files were changed.

## Commands and evidence

Executed from the Toolchain PR #132 worktree:

```bash
GOWORK=off go run ./backend/cmd/casp compile --package <ca-skills>/skills/5gc-file-transfer --registry ./registry --format json
GOWORK=off go run ./backend/cmd/casp compile --package <ca-skills>/skills/establish-pdu-session --registry ./registry --format json
```

The first exited 0; the second exited 1 for the single compile finding above. Full JSON reports are retained in `root-compile-report.json` and `child-compile-report.json`. Local authoring and repository gates from the same source candidate are recorded in [the initial qualification report](../20261029-createdsession-toolchain-consumer-qualification/README.md). These compile results are not production qualification, Capability Admission, cross-process integration, or live UE/5GC acceptance.
