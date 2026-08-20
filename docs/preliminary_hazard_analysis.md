# Preliminary Hazard Analysis

| Hazard | Cause | Existing control | Residual status |
|---|---|---|---|
| Unintended command release | operator error or bypass | RBAC, independent approval, mode/parameter interlocks, global inhibit | Demonstrator-contained |
| Hazardous single-person action | collusion/error | two distinct approvers plus flight-director release | Demonstrator-contained |
| Misleading telemetry | invalid/stale data | validity flag, stale detection, debounce and alarms | Requires mission-specific calibration |
| Loss of spacecraft function | undervoltage/thermal/radio fault | digital-twin FDIR and SAFE transition | Simulation only |
| Audit manipulation | record modification | SHA-256 chained audit evidence | Requires external protected storage operationally |
| Accidental real-equipment control | unintended adapter | no external command transport exists | Boundary must remain enforced |
