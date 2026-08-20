from pathlib import Path

import numpy as np
import pytest

from spacelinkops import load_scenario
from spacelinkops.sgp4prop import propagate_ecef


def test_public_tle_propagates_to_leo_state():
    pytest.importorskip("sgp4")
    cfg=load_scenario(Path(__file__).parents[1]/"scenarios/tle_sgp4.yaml")
    p,v=propagate_ecef(cfg.orbit.tle_line1,cfg.orbit.tle_line2,0)
    assert 6.4e6<np.linalg.norm(p)<8.0e6
    assert 6.5e3<np.linalg.norm(v)<9.0e3
