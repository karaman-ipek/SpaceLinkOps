"""Tests for the independent frame-transformation validation.

These lock in the reference agreement of the GMST rotation so that a future
change which silently degrades the frame conversion is caught in CI.
"""
from spacelinkops import validation


def test_gmst_matches_iau1982_reference_at_j2000():
    # Must agree with the canonical 280.46061837504 deg to well under 1e-6 deg.
    assert validation.gmst_reference_error_deg() < 1e-6


def test_sidereal_rotation_rate_is_correct():
    # Implied sidereal day must match 86164.0905 s to better than 0.01 s.
    assert validation.sidereal_rate_error_s() < 0.01


def test_rotation_matrix_is_orthonormal():
    assert validation.rotation_orthonormality_residual() < 1e-9


def test_rotation_sense_is_eastward():
    # Guards against a sign flip in the TEME->ECEF rotation.
    assert validation.rotation_sense_is_correct() is True


def test_eop_neglect_bound_is_reported_and_bounded():
    # The compact-GMST path should honestly report a few-hundred-metre bound
    # at LEO, not claim sub-metre (IERS-grade) accuracy.
    bound = validation.eop_neglect_bound_m()
    assert 100 < bound < 2000


def test_summary_is_complete():
    keys = set(validation.summary())
    assert {
        "gmst_j2000_error_deg", "sidereal_rate_error_s",
        "rotation_orthonormality_residual", "rotation_sense_correct",
        "eop_neglect_bound_m_at_leo",
    } <= keys
