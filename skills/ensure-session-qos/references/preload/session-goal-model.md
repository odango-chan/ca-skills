# Session goal model

The proactive goal of this Skill is: **a PDU Session exists and satisfies the requested QoS**. Create, modify, query, and reconcile operations are implementation steps; none of them independently establishes success.

The three postconditions answer separate questions: whether the session exists, whether the requested QoS is satisfied, and whether the user plane is actually usable. A mutation returning `COMMITTED` is therefore not enough; governed execution must still re-observe and prove all three Predicates.

User-plane connectivity is a final success gate, not a repair requirement owned by this Skill. If the Session and QoS already satisfy the request but `user_plane.connectivity.available=FAIL`, the Skill takes the zero-write verification path and returns failure rather than attempting unrelated repair.

Connectivity recovery belongs to a future goal such as `ensure-connectivity` or `restore-connectivity`.

Release/disconnection is a separate destructive goal and does not belong to this Skill. A flow that guarantees absence of the Session should be modeled separately, for example as `ensure-session-absent`.
