# Engineering model and validation basis

## Scope

SpaceLinkOps is a civilian educational system-performance simulator. It
supports both a transparent circular two-body model and real TLE propagation
through SGP4. It is appropriate for trade studies and portfolio
demonstrations, not flight operations, frequency coordination, or safety-critical
decisions.

## Equations

| Quantity | Model | Units |
|---|---|---|
| Mean motion | `n = sqrt(mu / a^3)` | rad/s |
| Circular position | `r = a[cos(nt), sin(nt), 0]` followed by rotations | m |
| Propagation delay | `range / c` | s |
| Free-space path loss | `20 log10(4 pi R f / c)` | dB |
| Received power | `Pt + Gt + Gr - Lfs - Lsystem - Latm` | dBW |
| Noise density | `-228.6 + 10 log10(Tsys)` | dBW/Hz |
| Carrier-to-noise density | `Pr - N0` | dB-Hz |
| Energy per bit to noise | `C/N0 - 10 log10(Rb)` | dB |

Constants use SI units. The WGS-84 equatorial radius is used with a spherical
Earth approximation. Earth rotation is included; oblateness, precession,
nutation, polar motion, atmospheric refraction, terrain masking and light-time
iteration are not.

## Packet and protocol model

Packet success uses the analytic uncoded BPSK/QPSK AWGN bit-error probability
and converts BER to packet error rate using packet length. Transfer frames add
spacecraft ID, virtual channel, sequence counter, payload length and a verified
CRC-16-CCITT. This is CCSDS-inspired teaching code, not a claim of bit-for-bit
conformance with every CCSDS managed parameter.

SGP4 returns TEME state vectors. The project applies a documented GMST rotation
for the ECEF visualization/access calculation. This rotation is validated
against the IAU-1982 GMST reference, and the error from neglecting full
Earth-orientation corrections is bounded explicitly (~540 m at LEO) in
`frame_validation.md`. High-precision Earth orientation work should use an
IERS-aware transformation library.

## Validation strategy

1. Unit tests compare FSPL against an independently calculated reference.
2. An overhead equatorial geometry case must return 90 degrees elevation and
   the configured orbital altitude as slant range.
3. Fixed random seeds must reproduce identical metrics.
4. A ground-station outage must never increase geometric availability.
5. The TEME-to-ECEF GMST rotation is validated against the IAU-1982 reference
   value and its neglected-Earth-orientation error is bounded (see
   `frame_validation.md`).
6. Further physics validation should compare access windows against GMAT/STK or
   an independent SGP4 reference and link results against a reviewed spreadsheet.

## Public references

- [CCSDS Blue Books](https://ccsds.org/publications/bluebooks/), including
  *TM Space Data Link Protocol*, CCSDS 132.0-B-3.
- [ITU-R P.525-5](https://www.itu.int/rec/R-REC-P.525-5-202411-I/en),
  *Calculation of Free-Space Attenuation*.
- [CelesTrak SGP4 verification tutorial](https://celestrak.org/software/tutorials/sgp4-verification.php).
- [JPL Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html), including
  its TLE/SGP4 limitations and user-defined TLE workflow.

The references define relevant concepts and standard equations; the example
scenario values are explicit design assumptions, not values mandated by them.
