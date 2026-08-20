# Requirements Traceability Matrix

| ID | Requirement | Implementation | Verification | Status |
|---|---|---|---|---|
| OPS-REQ-001 | The system shall prevent command release while global inhibit is active. | `src/spacelinkops/operations.py` | `tests/test_operations.py::test_inhibit_blocks_release` | MAPPED |
| OPS-REQ-002 | Hazardous commands shall require two independent approvals. | `src/spacelinkops/operations.py` | `tests/test_operations.py::test_hazardous_dual_control` | MAPPED |
| OPS-REQ-003 | A command submitter shall not approve the same command. | `src/spacelinkops/operations.py` | `tests/test_operations.py::test_submitter_cannot_approve` | MAPPED |
| OPS-REQ-004 | Released commands shall remain isolated from real external equipment. | `src/spacelinkops/operations.py` | `tests/test_operations.py::test_release_is_simulator_only` | MAPPED |
| TLM-REQ-001 | Telemetry limit violations shall respect configured debounce. | `src/spacelinkops/alarms.py` | `tests/test_alarms_twin.py::test_alarm_debounce_and_acknowledgement` | MAPPED |
| TLM-REQ-002 | The system shall identify stale telemetry. | `src/spacelinkops/alarms.py` | `tests/test_alarms_twin.py::test_stale_detection` | MAPPED |
| FDIR-REQ-001 | Critical spacecraft faults shall autonomously transition the twin to SAFE mode. | `src/spacelinkops/twin.py` | `tests/test_alarms_twin.py::test_critical_fault_enters_safe_mode` | MAPPED |
| AUD-REQ-001 | Operational actions shall form a verifiable tamper-evident audit chain. | `src/spacelinkops/assurance.py` | `tests/test_assurance.py::test_audit_chain_detects_tampering` | MAPPED |
| RF-REQ-001 | Link analysis shall calculate FSPL and modulation-specific packet error probability. | `src/spacelinkops/link.py; src/spacelinkops/rf.py` | `tests/test_models.py::test_fspl_reference_value; tests/test_protocol_rf.py::test_bpsk_reference_and_doppler` | MAPPED |
| ORB-REQ-001 | The system shall accept public TLEs and propagate them with SGP4. | `src/spacelinkops/sgp4prop.py` | `tests/test_sgp4.py::test_public_tle_propagates_to_leo_state` | MAPPED |
| ORB-REQ-002 | The TEME-to-ECEF conversion shall agree with the IAU-1982 GMST reference and report an explicit neglected-Earth-orientation error bound. | `src/spacelinkops/validation.py` | `tests/test_validation.py::test_gmst_matches_iau1982_reference_at_j2000` | MAPPED |
