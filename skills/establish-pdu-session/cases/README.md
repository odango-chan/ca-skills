# CreatedSession qualification cases

These 36 cases are currently **semantic qualification obligations**, not executable
Runtime fixtures.

They retain:

- the business scenario purpose;
- the PlanningContext shape;
- available resource declarations;
- expected planning status;
- expected terminal;
- expected Contract postconditions.

The historical exact trace and mock fixture sections were removed because they were
bound to the retired explicit execution graph. Keeping those node IDs would falsely
imply that the new authoring source had already been lowered and qualified.

Do not invent replacement flattened node IDs by hand.

After Toolchain/Runtime support for ordered `preconditions` and `postconditions` is
implemented:

1. lower the current `assurance/procedure.yaml` deterministically;
2. freeze stable authoring-to-runtime trace lineage;
3. rebind executable fixtures to the lowered identities;
4. execute all 36 cases through the real compile/link/admission/runtime path;
5. preserve each case's business expected outcome unless the authoring contract itself
   is intentionally reviewed and changed;
6. keep Case 32 as an actual action-budget enforcement obligation.

Case envelope/schema validation alone is not workflow execution or Runtime
qualification.
