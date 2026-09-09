# Authentication failures

Read this reference only when the Authentication stage fails and additional semantic interpretation is needed.

A synchronization failure means the UE and authentication side may have inconsistent sequence state; it does not imply that the subscriber is absent. An authentication response mismatch means the authentication goal was not satisfied and Security Context establishment must not continue. AUSF unavailability is a dependency failure and is not equivalent to the UE explicitly rejecting authentication.

If the side-effect state of an authentication mutation cannot be determined, preserve `OUTCOME_UNKNOWN`. The governed Registration Procedure owns the resulting transition and safety behavior; this reference does not authorize a direct retry.

This document explains failure meaning only. It does not define execution transitions, compensation policy, authorization exceptions, or Runtime behavior.
