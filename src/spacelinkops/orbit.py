"""Circular two-body orbit and spherical-Earth visibility model.

This transparent educational propagator is deterministic and deliberately does
not claim TLE/SGP4 fidelity. See docs/engineering_model.md.
"""
from __future__ import annotations

import math

import numpy as np

from .config import GroundStation, OrbitConfig
from .constants import EARTH_MU_M3_S2, EARTH_RADIUS_M, EARTH_ROTATION_RAD_S


def _r1(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]], dtype=float)

def _r3(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]], dtype=float)

def satellite_ecef(orbit: OrbitConfig, time_s: float) -> np.ndarray:
    if orbit.model == "sgp4":
        from .sgp4prop import propagate_ecef
        assert orbit.tle_line1 is not None and orbit.tle_line2 is not None
        return propagate_ecef(orbit.tle_line1, orbit.tle_line2, time_s)[0]
    # The config validator guarantees these are set on the two_body path.
    assert orbit.altitude_km is not None and orbit.inclination_deg is not None
    radius = EARTH_RADIUS_M + orbit.altitude_km * 1000
    mean_motion = math.sqrt(EARTH_MU_M3_S2 / radius**3)
    anomaly = math.radians(orbit.mean_anomaly_deg) + mean_motion * time_s
    perifocal = np.array([radius*math.cos(anomaly), radius*math.sin(anomaly), 0.0])
    eci = _r3(math.radians(orbit.raan_deg)) @ _r1(math.radians(orbit.inclination_deg)) @ _r3(math.radians(orbit.argument_of_perigee_deg)) @ perifocal
    return _r3(-EARTH_ROTATION_RAD_S*time_s) @ eci

def station_ecef(station: GroundStation) -> np.ndarray:
    lat, lon = map(math.radians, (station.latitude_deg, station.longitude_deg))
    return EARTH_RADIUS_M * np.array([math.cos(lat)*math.cos(lon), math.cos(lat)*math.sin(lon), math.sin(lat)])

def geometry(orbit: OrbitConfig, station: GroundStation, time_s: float) -> tuple[float,float]:
    site = station_ecef(station)
    delta = satellite_ecef(orbit, time_s) - site
    distance = float(np.linalg.norm(delta))
    cos_zenith = float(np.dot(delta/distance, site/np.linalg.norm(site)))
    elevation = math.degrees(math.asin(max(-1.0, min(1.0, cos_zenith))))
    return elevation, distance

def contact_windows(orbit: OrbitConfig, station: GroundStation, duration_s: int, step_s: int) -> list[dict]:
    samples = [(t, *geometry(orbit, station, t)) for t in range(0, duration_s+1, step_s)]
    windows, current = [], []
    for sample in samples:
        if sample[1] >= station.elevation_mask_deg:
            current.append(sample)
        elif current:
            windows.append(_window(current)); current=[]
    if current: windows.append(_window(current))
    return windows

def _window(samples: list[tuple]) -> dict:
    peak = max(samples, key=lambda x:x[1])
    return {"start_s": samples[0][0], "end_s": samples[-1][0], "peak_s": peak[0], "max_elevation_deg": peak[1], "min_range_km": min(x[2] for x in samples)/1000}
