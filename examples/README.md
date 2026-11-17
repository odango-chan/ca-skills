# CA-SL v1alpha5 candidate PDU/MAS Skills

**Language target:** `connectionagent.io/v1alpha5`  
**Normative source:** `odango-chan/ca-skills@12a9512a9eae006ad4578daf37ebe0bdf3070642`  
**Status:** Draft candidate; language not frozen; product and Owner qualification NOT_QUALIFIED.

This directory contains two candidate Skills:

- `establish-pdu-session`: conventional 5GC PDU Session establishment. Step 15 is represented by the v1alpha5 Node-entry Wait, with the Step 11 transfer Operation as its trigger, normalized `wait.output`, a fixed timeout branch, and a typed Step 17 response boundary after Step 16.
- `establish-pdu-session-mas`: source-aligned OpenAMSM MAS example. Its composite MAS Operation retains its own event correlation; it does not claim 3GPP semantics or end-to-end qualification.

The 5GC Skill declares an ordinary `integration` dependency as a placeholder for the trusted, version-pinned IngressCatalog package. The actual Ingress Operation export, request/response Schemas, Owner identity, trigger binding, correlation, and response mapping are not yet published. All `urn:example:` values are illustrative. Compiler linking and Build must fail closed until the exact trusted exports and deployment bindings exist.

This candidate is based on the v1alpha5 normative draft and the PDU/MAS example source. It is a source migration candidate, not a qualification report or a claim that all 36 EW conformance obligations have been executed.
