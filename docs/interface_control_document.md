# Interface Control Document

## External interface policy

Version 4 has no outbound device, radio, socket, serial, CAN, SpaceWire, REST or
message-bus command interface. `RELEASED_TO_SIMULATOR` is an internal state and
cannot address operational equipment.

## Scenario interface

YAML scenario inputs are validated by Pydantic. Physical quantities use SI
internally except fields whose names explicitly carry `_km`, `_deg`, `_db`,
`_dbi`, `_dbw`, `_hz` or `_bps`.

## Evidence interfaces

- Simulation results: versioned JSON
- Requirements: controlled YAML records with stable IDs
- Traceability: generated Markdown
- Audit records: ordered JSON-compatible objects linked by SHA-256 hashes
- Telemetry quality: validity, stale and limit-alarm states

## Prohibited integration

Adapters that transmit operational commands are intentionally outside the
repository scope. Adding one invalidates the demonstrator safety boundary and
requires a new hazard analysis, authorization model and independent review.
