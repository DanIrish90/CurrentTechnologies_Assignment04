# Data Model: Bureaucratic Document Workflow

**Feature**: `002-bureaucracy-document-workflow`

The workflow model is plain, deterministic Python state. It does not import Pygame, draw to a display, or depend on player movement implementation details.

## Canonical terminology

- **Civil Servant** is the canonical term for a wave participant.
- **Document** is the canonical term for any carried workflow item.
- **Permit** is a document type issued by Civil Servant 1 in wave 2.
- **Handover** is an explicit interaction attempt to deliver the carried document to a target Civil Servant.
- **Workflow Step** is the ordered requirement assigned to one Civil Servant.

## Value types

### `DocumentType`

An enumerated data value describing a document's role.

| Value | Meaning |
|---|---|
| `INITIAL_DOCUMENT` | The document supplied by the central document source at the start of a workflow. |
| `PERMIT` | The document issued by Civil Servant 1 in wave 2 and required by Civil Servant 2. |

Additional document types must be addable as structured values without changing the handover algorithm.

### `Document`

A carryable workflow item.

| Field | Type | Rules |
|---|---|---|
| `document_type` | `DocumentType` | Required. Determines which workflow steps can accept it. |
| `workflow_id` | string | Identifies the wave/workflow that owns the document. |
| `intended_servant_id` | string or null | Optional target identity; when present, a different servant must reject it. |
| `issued_by_servant_id` | string or null | Identifies the successful handover that produced it. |

Rules:

- A carried document belongs to the active workflow.
- A handover consumes a matching document exactly once.
- An invalid handover never mutates or replaces the document.

### `WorkflowStep`

One ordered Civil Servant requirement.

| Field | Type | Rules |
|---|---|---|
| `order` | integer | Starts at 1 and increases without gaps. |
| `servant_id` | string | Unique within the wave. |
| `required_document_type` | `DocumentType` | The document accepted by this step. |
| `required_document_source` | `CENTRAL_SOURCE` or `PREVIOUS_HANDOVER` | Identifies how the player obtains the document. |
| `issued_document_type` | `DocumentType` or null | Optional document created by a successful handover. |
| `served` | boolean | False until the correct explicit handover succeeds. |

Rules:

- A step can be served only if all earlier steps are served.
- A served step cannot be served again or issue another reward.
- The next active step is the first unserved step in order.

### `CivilServant`

A positioned participant derived from a workflow step.

| Field | Type | Rules |
|---|---|---|
| `id` | string | Unique within the active wave. |
| `display_name` | string | Readable player-facing label such as `Civil Servant 1`. |
| `position` | world position | Used by the presentation/world layer for interaction range. |
| `step_order` | integer | Links the servant to its ordered workflow step. |
| `served` | boolean | Mirrors the step's completion state in the UI snapshot. |

The pure workflow does not determine physical collision; the existing world/movement layer determines whether the player is in interaction range.

### `WaveDefinition`

Immutable configuration for one wave.

| Field | Type | Rules |
|---|---|---|
| `wave_number` | integer | Positive and unique in the supported definition set. |
| `steps` | ordered sequence of `WorkflowStep` | Contains exactly `wave_number` steps for the supported escalation rule. |
| `servants` | ordered sequence of `CivilServant` | Contains exactly `wave_number` unique servants. |

Validation:

- Wave 1 has exactly one step: the central source provides `INITIAL_DOCUMENT` to Civil Servant 1; no replacement document is required.
- Wave 2 has exactly two steps: Civil Servant 1 accepts `INITIAL_DOCUMENT` and issues `PERMIT`; Civil Servant 2 accepts that `PERMIT`.
- Every step's required document is either supplied by the central source or issued by an earlier step.
- All servant identifiers and step orders are unique and contiguous.
- The final step does not issue an unresolved requirement for the current wave.

### `WaveProgress`

Mutable-at-the-boundary, immutable-between-transitions runtime workflow state.

| Field | Type | Rules |
|---|---|---|
| `definition` | `WaveDefinition` | The active wave configuration. |
| `carried_document` | `Document` or null | At most one document. Must belong to `definition`. |
| `feedback` | `Feedback` | Latest player-facing result. |
| `phase` | `ACTIVE`, `COMPLETION_FEEDBACK`, or `TRANSITIONING` | Controls allowed actions and timer behavior. |
| `transition_remaining` | float | Zero during `ACTIVE`; starts at 10.0 after final handover and decreases with elapsed time. |

State transitions:

```text
ACTIVE
  -> ACTIVE after valid document collection when the current step needs a central-source document
ACTIVE
  -> ACTIVE after invalid collection or handover, preserving progress and carried document
ACTIVE
  -> COMPLETION_FEEDBACK after the final valid handover
COMPLETION_FEEDBACK
  -> TRANSITIONING while transition_remaining > 0
TRANSITIONING
  -> ACTIVE for the next WaveDefinition when transition_remaining reaches 0
```

During `COMPLETION_FEEDBACK` and `TRANSITIONING`, the game may continue movement and rendering, but collection and handover actions for the completed wave are rejected as inactive.

### `HandoverResult`

The pure result of a collection or handover attempt.

| Field | Type | Meaning |
|---|---|---|
| `accepted` | boolean | Whether the requested action changed valid workflow progress. |
| `reason` | enum/string | Stable reason such as `NO_DOCUMENT`, `WRONG_DOCUMENT`, `OUT_OF_ORDER`, `ALREADY_SERVED`, or `ACCEPTED`. |
| `feedback` | `Feedback` | Player-facing message and severity. |
| `issued_document` | `Document` or null | New document created by a successful step. |
| `wave_completed` | boolean | True only on the final valid handover. |

## Initial definitions

```text
Wave 1:
  Civil Servant 1: requires INITIAL_DOCUMENT from CENTRAL_SOURCE
  Successor: none

Wave 2:
  Civil Servant 1: requires INITIAL_DOCUMENT from CENTRAL_SOURCE
                   issues PERMIT on success
  Civil Servant 2: requires PERMIT from PREVIOUS_HANDOVER
  Successor: none
```

## Invariants

- The active wave contains exactly N unique Civil Servants for wave N.
- Only the first unserved workflow step can be served.
- A document mismatch, missing document, duplicate handover, or out-of-order attempt leaves `carried_document`, served states, and wave number unchanged.
- A successful handover consumes its input document exactly once.
- A permit is issued exactly once by the successful wave 2 Civil Servant 1 handover.
- A wave completes only when all steps are served.
- The next wave starts exactly 10 elapsed seconds after final-handover completion feedback begins.
- No active workflow can be created from an invalid or unsolvable definition.
