"""Independent validation of the frame-transformation approximation.

This module is deliberately additive and non-invasive: it does not change how
``sgp4prop`` propagates. It exists to put a *number* on the honest limitation
already stated in the README and engineering model, namely that the
TEME-to-ECEF conversion uses a compact GMST rotation and neglects the
Earth-orientation corrections (precession-nutation of the equinox and polar
motion) that a full IERS-aware pipeline would apply.

Two things are validated here, and they are kept separate on purpose:

1. The SGP4 propagation of TEME position/velocity is provided by the ``sgp4``
   package, which is independently validated by its maintainers against the
   Vallado "Revisiting Spacetrack Report #3" reference vectors. We do not
   re-derive that; we rely on it and say so.

2. The GMST rotation is *our* code. It is checked against the authoritative
   IAU-1982 GMST value at the J2000.0 epoch and against the sidereal-rotation
   rate, and its rotation matrix is checked for orthonormality and correct
   sense of Earth rotation. The neglected-EOP error is then bounded from the
   published magnitudes of the terms that are omitted.

References
----------
- D. A. Vallado, *Fundamentals of Astrodynamics and Applications*, 4th ed.,
  GMST (IAU-1982), Eq. 3-47; the canonical J2000.0 value is
  280.46061837504 degrees.
- IERS Conventions (2010): polar motion is at the sub-arcsecond level
  (~0.3 arcsec typical) and the equation of the equinoxes (nutation in right
  ascension) is dominated by the ~17 arcsec nutation-in-longitude term scaled
  by cos(obliquity), i.e. ~16 arcsec. Neglecting these bounds the along-track
  rotation error to a few hundred metres at a LEO geocentric radius (see
  ``eop_neglect_bound_m``). This is exactly why the compact-GMST path is
  documented as unsuitable for precision or operational orbit determination.
"""
from __future__ import annotations

import math

import numpy as np

from .constants import EARTH_ROTATION_RAD_S
from .sgp4prop import _gmst

# Authoritative reference constants (see module docstring for sources).
GMST_J2000_DEG = 280.46061837504
SIDEREAL_DAY_S = 86164.0905
ARCSEC_TO_RAD = math.pi / (180.0 * 3600.0)


def gmst_reference_error_deg() -> float:
    """Absolute error, in degrees, of our GMST at the J2000.0 epoch against
    the canonical IAU-1982 value. A correct implementation is well under
    1e-6 deg."""
    computed_deg = math.degrees(_gmst(2451545.0)) % 360.0
    return abs(computed_deg - GMST_J2000_DEG)


def sidereal_rate_error_s() -> float:
    """Error, in seconds, of the sidereal day implied by our GMST rate term
    against the known sidereal day. Sensitive to the 360.98564736629 deg/day
    coefficient."""
    # Recover the mean rate (deg per day of UT) from a small step, unwrapping
    # the angle so the modulo-360 boundary does not corrupt the difference.
    dt_days = 0.01
    raw = math.degrees(_gmst(2451545.0 + dt_days)) - math.degrees(_gmst(2451545.0))
    delta_deg = (raw + 180.0) % 360.0 - 180.0
    rate_deg_per_day = delta_deg / dt_days
    implied_sidereal_day = 360.0 / rate_deg_per_day * 86400.0
    return abs(implied_sidereal_day - SIDEREAL_DAY_S)


def _teme_to_ecef_matrix(jd: float) -> np.ndarray:
    """Reconstruct the same rotation used inside ``propagate_ecef`` so its
    properties can be checked directly, without needing the sgp4 package."""
    a = _gmst(jd)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])


def rotation_orthonormality_residual(jd: float = 2451545.0) -> float:
    """Max absolute deviation of R @ R.T from the identity. A proper rotation
    is orthonormal, so this must be at machine-precision level."""
    r = _teme_to_ecef_matrix(jd)
    return float(np.max(np.abs(r @ r.T - np.eye(3))))


def rotation_sense_is_correct(jd: float = 2451545.0, dt_s: float = 1.0) -> bool:
    """The ECEF frame rotates with the Earth (eastward, +Z). Advancing time
    must rotate a fixed TEME vector clockwise about +Z when viewed from the
    north, i.e. the ECEF longitude of a fixed inertial point must *decrease*.
    This guards against a sign flip in the GMST rotation."""
    fixed_teme = np.array([1.0, 0.0, 0.0])
    lon0 = math.atan2(*(_teme_to_ecef_matrix(jd) @ fixed_teme)[[1, 0]])
    lon1 = math.atan2(*(_teme_to_ecef_matrix(jd + dt_s / 86400.0) @ fixed_teme)[[1, 0]])
    # unwrap the small step
    dlon = (lon1 - lon0 + math.pi) % (2 * math.pi) - math.pi
    return dlon < 0


def eop_neglect_bound_m(radius_m: float = 6.9e6, neglected_arcsec: float = 16.1) -> float:
    """Upper bound, in metres, on the position error introduced by neglecting
    Earth-orientation corrections, at a given geocentric radius.

    The dominant neglected term is the equation of the equinoxes (nutation in
    right ascension): the ~17 arcsec nutation-in-longitude scaled by
    cos(obliquity ~= 23.44 deg) gives ~15.8 arcsec, and adding ~0.3 arcsec of
    typical polar motion gives ~16.1 arcsec combined. This angular offset maps
    to a tangential displacement of ``radius * angle``, i.e. a few hundred
    metres at a nominal LEO radius. Quoting this bound is the honest way to
    characterise the compact-GMST path rather than claiming IERS-grade
    accuracy."""
    return radius_m * neglected_arcsec * ARCSEC_TO_RAD


def summary() -> dict:
    """Machine-readable validation summary, suitable for release evidence."""
    return {
        "gmst_j2000_error_deg": gmst_reference_error_deg(),
        "sidereal_rate_error_s": sidereal_rate_error_s(),
        "rotation_orthonormality_residual": rotation_orthonormality_residual(),
        "rotation_sense_correct": rotation_sense_is_correct(),
        "earth_rotation_rad_s": EARTH_ROTATION_RAD_S,
        "eop_neglect_bound_m_at_leo": eop_neglect_bound_m(),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summary(), indent=2))
