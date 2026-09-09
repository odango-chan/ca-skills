# Security failures

Read this reference only when Security Context establishment fails.

Distinguish an explicit UE rejection, integrity verification failure, dependency timeout, and an outcome whose side-effect state is unknown. Successful Authentication must not be used to infer that the Security Context was established; the final state still requires independent governed proof.

If the Security Context mutation returns `OUTCOME_UNKNOWN`, preserve that outcome and let the governed Procedure apply its declared safety semantics. Do not infer commitment merely because Authentication succeeded.

This document explains failure meaning only. It does not authorize bypassing Authorization, Assurance, Provider policy, or Runtime execution rules.
