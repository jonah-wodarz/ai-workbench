# Default vocabulary

Use these values when the project's conventions define none.

| Item | Values |
|---|---|
| System status | `idea` · `drafting` (working notes allowed) · `settled` (L2 decided; changes need a decision entry) · `validated` (rules confirmed by a probe, a prototype or the implementation) · `locked` (frozen on purpose) · `deferred` |
| Rule tag | `locked` (decided) · `leaning` (only under *Provisional rules*, citing its open question) · `placeholder` (a number that must stay for now) · `conflicting` (contradicts another rule and is knowingly left open; cites the other rule's ID) |
| Question tag | `blocking` (gates the next status or layer; listed in the open-questions index) · `major` · `minor` · `needs-build` (closable only by building or playing) · `deferred` |
| IDs | Rule `ORD-R7`, question `ORD-Q2`, interface item `ORD-I1`, decision `D-ORD-006`. An ID is never reused |

## Parking lot and out of scope

- **Parking lot**: in-scope ideas that are not ready yet. One line each, grouped by system and tagged with the target layer: `- [repairs, L3] express repairs cost a surcharge`. Location: `parking-lot.md` at the docs root, or a *Parked* section in the owning spec. When the system reaches that layer, move the entries into the spec and delete them from the lot.
- **Out of scope**: ideas ruled out of the project. One line each with the reason, in an *Out of scope* section of the parking lot or the vision's *Scope*. They return only when the project's scope is redrawn.
