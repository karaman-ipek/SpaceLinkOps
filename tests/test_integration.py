from pathlib import Path

from spacelinkops import load_scenario, run_scenario

ROOT=Path(__file__).parents[1]

def test_nominal_is_deterministic():
    cfg=load_scenario(ROOT/"scenarios/nominal.yaml")
    a,b=run_scenario(cfg),run_scenario(cfg)
    assert a.metrics==b.metrics
    assert len(a.contacts)==3
    assert 0<=a.metrics["command_completion_rate"]<=1
    assert any(c["state"]=="ACKNOWLEDGED" for c in a.commands)
    assert all(c["history"][0]["state"]=="CREATED" for c in a.commands)

def test_failure_scenario_reduces_or_preserves_availability():
    nominal=run_scenario(load_scenario(ROOT/"scenarios/nominal.yaml"))
    stress=run_scenario(load_scenario(ROOT/"scenarios/resilience.yaml"))
    assert stress.metrics["availability"]<=nominal.metrics["availability"]
