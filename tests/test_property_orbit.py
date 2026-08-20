"""Property-based tests for two-body geometry.

The main target here is the elevation calculation in geometry(): it takes
asin() of a dot product of two unit vectors, which floating-point rounding
can occasionally push a hair outside [-1, 1]. This fuzzes altitude,
inclination, station location and time broadly (including exact overhead
passes) to make sure that never raises again.
"""
from hypothesis import given, settings
from hypothesis import strategies as st

from spacelinkops.config import GroundStation, OrbitConfig
from spacelinkops.orbit import geometry

_altitude_km = st.floats(min_value=101, max_value=49999, allow_nan=False, allow_infinity=False)
_inclination_deg = st.floats(min_value=0, max_value=180, allow_nan=False, allow_infinity=False)
_angle_deg = st.floats(min_value=0, max_value=360, allow_nan=False, allow_infinity=False)
_lat_deg = st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False)
_lon_deg = st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
_time_s = st.floats(min_value=0, max_value=1e7, allow_nan=False, allow_infinity=False)


@given(
    altitude_km=_altitude_km,
    inclination_deg=_inclination_deg,
    raan_deg=_angle_deg,
    argument_of_perigee_deg=_angle_deg,
    mean_anomaly_deg=_angle_deg,
    lat_deg=_lat_deg,
    lon_deg=_lon_deg,
    time_s=_time_s,
)
@settings(max_examples=300)
def test_geometry_never_raises_and_elevation_in_range(
    altitude_km, inclination_deg, raan_deg, argument_of_perigee_deg,
    mean_anomaly_deg, lat_deg, lon_deg, time_s,
):
    orbit = OrbitConfig(
        altitude_km=altitude_km, inclination_deg=inclination_deg, raan_deg=raan_deg,
        argument_of_perigee_deg=argument_of_perigee_deg, mean_anomaly_deg=mean_anomaly_deg,
    )
    station = GroundStation(name="Fuzz", latitude_deg=lat_deg, longitude_deg=lon_deg)
    elevation, distance = geometry(orbit, station, time_s)
    assert -90.0 <= elevation <= 90.0
    assert distance > 0


def test_geometry_handles_exact_overhead_pass():
    """Regression test for the asin domain-error bug: satellite directly
    overhead an equatorial station should give elevation ~90 degrees, not
    crash on floating-point rounding above 1.0."""
    orbit = OrbitConfig(altitude_km=550, inclination_deg=0)
    station = GroundStation(name="Equator", latitude_deg=0, longitude_deg=0)
    elevation, _distance = geometry(orbit, station, 0)
    assert abs(elevation - 90.0) < 1e-6
