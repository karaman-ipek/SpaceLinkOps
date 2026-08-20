# Frame-Transformation Validation

This note quantifies the accuracy of the TEME-to-ECEF conversion used on the
SGP4 path, turning the qualitative limitation stated in the README and
engineering model into measured numbers and an explicit error bound. It is
produced by `src/spacelinkops/validation.py` and locked in by
`tests/test_validation.py`; run `python -m spacelinkops.validation` to
regenerate the summary.

## What is and is not being validated

The SGP4 path has two distinct stages, validated separately and honestly:

1. **SGP4 propagation (TEME position/velocity).** This is delegated to the
   `sgp4` package, which is independently validated by its maintainers against
   the Vallado *Revisiting Spacetrack Report #3* reference vectors. This
   project relies on that validation and does not re-derive it.

2. **The GMST TEME-to-ECEF rotation.** This is code local to this project and
   is the piece validated here.

## Results

| Check | Result | Reference |
|---|---|---|
| GMST at J2000.0 epoch | error < 1e-6 deg (measured ~5e-9 deg) | IAU-1982, canonical 280.46061837504 deg (Vallado Eq. 3-47) |
| Sidereal rotation rate | implied sidereal day within 0.002 s | 86164.0905 s |
| Rotation orthonormality | \|R Rᵀ − I\| ~ 1e-18 | proper rotation |
| Rotation sense | eastward (+Z), correct | Earth rotation direction |
| Neglected-EOP bound at LEO | ~540 m | see below |

## The neglected-Earth-orientation error bound

The compact GMST rotation deliberately omits the full Earth-orientation
pipeline: precession-nutation of the equinox and polar motion. The dominant
omitted term is the equation of the equinoxes (nutation in right ascension):
the ~17 arcsec nutation-in-longitude scaled by cos(obliquity ≈ 23.44°) gives
~15.8 arcsec, and adding ~0.3 arcsec of typical polar motion gives ~16.1
arcsec combined. At a nominal LEO geocentric radius (~6.9 × 10⁶ m) this angular
offset maps to a tangential position error of

    error ≈ radius × angle ≈ 6.9e6 m × 16.1 arcsec × (π / 648000) ≈ 540 m.

This is the honest characterisation of the compact-GMST path: adequate for the
contact-geometry, elevation-mask and link-budget trade studies this tool is
built for, and explicitly **not** adequate for precision orbit determination,
conjunction assessment, or operational planning, which require an IERS-aware
frame library (full precession-nutation model plus published EOP data).

## Why this matters

Contact-window boundaries in this simulator are driven by an elevation mask
(typically ≥ 10°), where the geometry changes by degrees over tens of seconds.
A few hundred metres of frame error at LEO is far below the sensitivity of that
threshold, so it does not materially affect access windows, availability, or
link-margin conclusions. The bound is stated so that a user knows precisely
where the model stops being trustworthy rather than having to guess.
