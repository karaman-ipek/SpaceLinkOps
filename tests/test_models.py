import math

import numpy as np

from spacelinkops.config import GroundStation, OrbitConfig
from spacelinkops.link import free_space_path_loss_db, packet_success_probability
from spacelinkops.orbit import geometry
from spacelinkops.telemetry import generate_telemetry


def test_fspl_reference_value():
    assert math.isclose(free_space_path_loss_db(1_000_000,2.2e9),159.30,abs_tol=0.02)

def test_probability_monotonic():
    assert packet_success_probability(-5)<packet_success_probability(0)<packet_success_probability(5)

def test_overhead_geometry():
    o=OrbitConfig(altitude_km=550,inclination_deg=0)
    s=GroundStation(name="Equator",latitude_deg=0,longitude_deg=0)
    elevation,distance=geometry(o,s,0)
    assert math.isclose(elevation,90,abs_tol=1e-6)
    assert math.isclose(distance,550_000,abs_tol=1)

def test_anomaly_detector_finds_injected_event():
    rows=generate_telemetry(np.arange(0,7200,60),42)
    assert any(r["anomaly"] for r in rows)
