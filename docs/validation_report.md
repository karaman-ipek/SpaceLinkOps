# Validation and resilience report — v4.0

The deterministic checks and two 24-hour integration scenarios were executed
on 20 August 2026.

| Metric | Nominal | Resilience stress | Direction |
|---|---:|---:|---|
| Command completion | 23.88% | 12.11% | degraded |
| Telemetry delivery | 4.72% | 1.67% | degraded |
| Ground availability | 5.21% | 3.84% | degraded |
| Mean delivered-packet latency | 0.423 s | 0.902 s | degraded |
| P95 latency | 0.582 s | 3.081 s | degraded |
| In-contact packet success | 92.57% | 53.15% | degraded |
| Station switches | 5 | 3 | degraded |
| Maximum absolute predicted Doppler | 48.47 kHz | 46.28 kHz | bounded |

The command rate intentionally exceeds available contact capacity, so completion
rate exercises queue expiry and scheduling rather than reporting an artificially
perfect demonstration. A 20-run nominal ensemble produced a mean command
completion of 24.19%, standard deviation 0.60 percentage points, and a
5th–95th percentile interval of 23.51%–24.93%.

## Ground-station ablation

| Removed station | Availability change | Command-completion change |
|---|---:|---:|
| Kourou | −1.37 pp | −4.84 pp |
| Hartebeesthoek | −1.88 pp | −7.61 pp |
| Santiago | −1.97 pp | −7.61 pp |

This identifies Santiago as the largest geometric availability contributor and
shows that Hartebeesthoek and Santiago are tied for command-capacity impact in
the configured workload.

Checks passed:

- source and dashboard compile;
- FSPL reference value within 0.02 dB;
- overhead geometry returns 90° elevation and 550 km range;
- packet probability is monotonic with margin;
- fixed seed gives deterministic output;
- injected outage reduces availability;
- injected terrestrial delay raises latency;
- commands contain auditable lifecycle histories;
- injected telemetry anomaly is detected.
- CRC-16-CCITT passes the `123456789 → 0x29B1` check and rejects corruption;
- BPSK at 0 dB matches the analytic BER reference;
- the public TLE scenario is exercised by CI when the SGP4 dependency is present.

These checks validate software behavior and internal consistency. They do not
constitute flight qualification. The TEME-to-ECEF frame conversion is validated
against the IAU-1982 GMST reference with an explicit ~540 m neglected-EOP error
bound at LEO (see `frame_validation.md`); independent SGP4/GMAT access-window
validation remains the primary future physics upgrade.

## Version 4 operational-assurance evidence

- 11/11 controlled requirements map to implementation and named tests.
- Global inhibit blocks both submission and release paths.
- Hazardous commands cannot release with only one independent approval.
- Submitter self-approval is rejected.
- Released commands terminate at `RELEASED_TO_SIMULATOR`.
- Telemetry red-limit debounce, acknowledgement and stale detection pass.
- Undervoltage, overtemperature and radio faults cause SAFE-mode entry.
- Audit hash-chain verification passes and deliberate tampering is detected.
- CI generates coverage output, dependency audit results and a CycloneDX SBOM.
