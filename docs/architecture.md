# Architecture

The dependency direction is intentionally one-way:

1. `config.py` validates scenario inputs.
2. `orbit.py` produces satellite position, geometry and access windows.
3. `link.py` turns slant range into link metrics and packet probability.
4. `engine.py` schedules traffic, selects the best visible station, injects
   failures and produces metrics/risks.
5. `scheduler.py` implements the auditable command state machine.
6. `network.py` performs graph-cut criticality and FMEA ranking.
7. `telemetry.py` generates housekeeping streams and robust anomaly scores.
8. `cli.py` and `dashboard/app.py` are thin presentation layers.
9. `sgp4prop.py` isolates public-TLE propagation and frame conversion.
10. `rf.py` contains modulation-specific BER/PER and Doppler physics.
11. `frames.py` owns sequence, virtual-channel and CRC integrity behavior.
12. `trades.py` performs automated ground-station ablation studies.

This separation allows the orbit and packet approximations to be replaced
without rewriting the interface or scenario format.

## Operational assurance layer

The modules above cover performance and resilience. A second, independent layer
covers mission-operations assurance:

13. `operations.py` provides the command authority: role-based access control,
    two-person approval, hazardous-command dual control, mode and parameter
    interlocks, and a global inhibit.
14. `alarms.py` performs telemetry limit monitoring with debounce,
    acknowledgement and stale-data detection.
15. `twin.py` is a small deterministic spacecraft digital twin with autonomous
    safe-mode FDIR.
16. `assurance.py` maintains the SHA-256 tamper-evident audit chain.
17. `traceability.py` generates the requirements traceability matrix.
18. `validation.py` independently validates the TEME-to-ECEF frame conversion
    against the IAU-1982 GMST reference and bounds its neglected-EOP error.
19. `constants.py` holds the SI physical constants shared across the codebase.

## Event semantics

- A command is generated at each configured command interval.
- Telemetry is generated independently at its configured interval.
- If no operational station is visible, the event fails with zero attempts.
- Otherwise the station with the highest link margin is selected.
- Attempts continue until success or the retry limit is exhausted.
- Successful command latency includes round-trip propagation to represent an
  acknowledgement; telemetry uses one-way propagation.
- Network delay windows add deterministic latency to isolate terrestrial
  network effects from RF effects.
