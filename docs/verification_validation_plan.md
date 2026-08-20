# Verification and Validation Plan

1. Run compilation and static checks on every change.
2. Generate the requirements traceability matrix; fail on missing artifacts.
3. Run unit tests for physics, protocols, RBAC, interlocks, alarms, FDIR and audit integrity.
4. Run nominal and resilience integration scenarios with fixed seeds.
5. Run Monte Carlo ensembles and retain percentile evidence.
6. Run station-ablation trade studies.
7. Exercise the public TLE case when SGP4 is installed.
8. Build the container from a clean environment.
9. Archive scenario, software revision, dependency manifest and results together.
10. Run dependency vulnerability audit and publish a CycloneDX SBOM in CI.

Acceptance of this plan demonstrates internal consistency only. Flight
qualification additionally requires an identified mission, controlled hardware,
independent verification, organizational approval and applicable assurance
standards.
