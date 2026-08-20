# Software Requirements Specification (demonstrator)

## Purpose and boundary

SpaceLinkOps shall demonstrate assurance-oriented satellite mission operations
without providing any interface capable of transmitting to real spacecraft,
antennas, radios or ground equipment. Simulation release is the terminal state.

## Safety objectives

- A command must be known, parameter-valid and permitted in the current mode.
- A submitter must not approve their own command.
- Hazardous commands require two independent approvals.
- Only the flight-director role may release an approved command.
- Global inhibit must dominate every release path.
- Every operational action must enter a verifiable audit chain.
- Critical digital-twin faults must lead to a deterministic SAFE transition.
- Invalid or stale telemetry must not be silently treated as nominal.

The controlled requirement set is stored in `requirements/requirements.yaml`.
The generated mapping is `docs/traceability_matrix.md`.
