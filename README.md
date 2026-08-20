# SpaceLinkOps

**An assurance-oriented, offline satellite C3 and TT&C mission-operations demonstrator.**

SpaceLinkOps v4 models a LEO spacecraft, three geographically separated ground
stations, contact windows, command uplink, telemetry downlink, RF link margin,
packet success, retries, ground-station handover, network delay, station outage,
engineering risks and Monte Carlo uncertainty.

The seven-view mission-control dashboard combines an interactive 3-D Earth/orbit,
dynamic RF margin, contact-aware command state machine, explainable telemetry
anomaly detection, graph-cut criticality, ranked FMEA and resilience ensembles.

The operational assurance layer adds role-based command authority, independent
approval, hazardous-command dual control, mode and parameter interlocks, global
inhibit, telemetry alarm management, deterministic safe-mode FDIR, a digital
twin, tamper-evident audit records and generated requirements traceability.

> **Safety boundary:** this repository deliberately contains no interface that
> can transmit to real spacecraft, radios, antennas or ground equipment.

## What it demonstrates

- Orbital access and elevation-mask analysis
- Real TLE/SGP4 propagation with explicit TEME/ECEF handling
- SI-unit link budget: FSPL, received power, C/N0, Eb/N0, SNR and margin
- Deterministic discrete-event command and telemetry simulation
- Availability, latency, success, contact-time and handover metrics
- Station-outage, link-degradation and terrestrial-delay scenarios
- Automated risk/gap flags and Monte Carlo analysis
- Full `CREATED → QUEUED → UPLINKED → RECEIVED → EXECUTED → ACKNOWLEDGED` lifecycle
- Robust median-absolute-deviation telemetry anomaly detection
- BPSK/QPSK AWGN BER-to-packet-error physics and carrier Doppler prediction
- CRC-16 protected spacecraft/virtual-channel transfer frames
- Graph-cut single-point-of-failure analysis and ranked FMEA
- Automated leave-one-station-out ground-segment trade study
- RBAC command console with two-person approval and flight-director release
- Global command inhibit, spacecraft-mode interlocks and parameter constraints
- Telemetry yellow/red limits, debounce, acknowledgement and stale-data detection
- Digital-twin fault injection with autonomous SAFE-mode transition
- SHA-256 tamper-evident operational audit chain
- Requirements → implementation → verification traceability matrix
- SRS, ICD, V&V plan and preliminary hazard analysis
- Interactive seven-tab Streamlit/Plotly mission-control dashboard with 3-D Earth

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dashboard,dev]"
spacelinkops scenarios/nominal.yaml --output outputs/nominal.json --monte-carlo 100 --station-ablation
streamlit run dashboard/app.py
```

The core install (NumPy, Pydantic, PyYAML and SGP4) covers both propagators and
the full simulation. The Streamlit/Plotly dashboard is an optional extra.

## Scenarios

`nominal.yaml` is the baseline. `resilience.yaml` injects a full-day Kourou
outage, a terrestrial delay window and a 3 dB margin penalty. Copy a
scenario to run your own sensitivity study; validation rejects invalid
coordinates, non-positive physical quantities and unknown outage stations.

## Validation

```bash
pytest -q
ruff check src tests
python -m compileall -q src dashboard
```

The core tests cover a reference FSPL value, overhead geometry, probability
monotonicity, deterministic results and outage availability. Property-based
tests (Hypothesis) additionally fuzz the link budget, orbit geometry and
transfer-frame codec across their full valid input ranges. See
[`docs/engineering_model.md`](docs/engineering_model.md) for equations,
assumptions, limitations and authoritative public references. The executed
nominal/stress comparison is in [`docs/validation_report.md`](docs/validation_report.md).

The TEME-to-ECEF frame conversion on the SGP4 path is validated against the
IAU-1982 GMST reference and the neglected-Earth-orientation error is bounded
explicitly (~540 m at LEO) in
[`docs/frame_validation.md`](docs/frame_validation.md); run
`python -m spacelinkops.validation` to reproduce the numbers.

## Repository map

```text
src/spacelinkops/       physics, configuration, simulation and CLI
scenarios/              nominal and resilience YAML configurations
dashboard/              Streamlit mission-control UI
tests/                  unit and integration validation
docs/                   architecture and engineering model
requirements/           controlled assurance requirements with stable IDs
scripts/                evidence and traceability generation
.github/workflows/      automated quality checks
```

## Propagators

Use `model: two_body` for transparent synthetic trade studies, or `model: sgp4`
with two TLE lines for public-catalogue realism. `scenarios/tle_sgp4.yaml`
contains a reproducible public TLE example. TLEs are mean elements tied to SGP4;
they must not be treated as osculating elements or extrapolated indefinitely.

## Important limitations

The SGP4 path uses a compact GMST TEME-to-ECEF rotation; high-precision Earth
orientation requires an IERS-aware frame library. RF error probabilities are
uncoded AWGN BPSK/QPSK models rather than a claim about a particular flight
modem or coding chain. Results remain for education and early trade studies—not
operational planning, licensing or safety-critical decisions.

## Responsible scope

SpaceLinkOps does not implement weapon targeting, electronic attack, offensive
cyber capabilities, interference procedures or classified/restricted
architectures.

## Assurance status

The accurate description is **flight-software-inspired, assurance-oriented,
offline mission-operations demonstrator**. It is not flight-qualified. Flight
qualification is a mission- and organization-specific evidence process involving
controlled requirements, applicable standards, independent verification,
representative hardware and formal acceptance—not a repository feature flag.

## License

MIT © 2026 Ipek Karaman
