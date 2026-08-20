"""Edge-case regression tests for run_scenario().

These target configurations that are technically valid per the pydantic
schema but stress the engine's assumptions: no ground stations at all, a
station that's outed for the entire run, and a run shorter than one time
step. All of these should complete without raising and should return sane,
zeroed-out metrics rather than crashing.
"""
from spacelinkops.config import (
    FailureConfig,
    GroundStation,
    OrbitConfig,
    RadioConfig,
    ScenarioConfig,
    TrafficConfig,
)
from spacelinkops.engine import run_scenario
from spacelinkops.trades import station_ablation

_ORBIT = OrbitConfig(altitude_km=550, inclination_deg=53)
_RADIO = RadioConfig(
    frequency_hz=2.2e9, transmit_power_w=2, spacecraft_antenna_gain_dbi=-5,
    bandwidth_hz=100_000, data_rate_bps=19_200,
)
_TRAFFIC = TrafficConfig(
    command_interval_s=300, command_size_bits=2048,
    telemetry_interval_s=60, telemetry_size_bits=8192,
)
_STATION = GroundStation(name="Solo", latitude_deg=5.236, longitude_deg=-52.775)


def _scenario(name, ground_stations, duration_s=3600, time_step_s=20, failures=None):
    return ScenarioConfig(
        name=name, duration_s=duration_s, time_step_s=time_step_s,
        orbit=_ORBIT, ground_stations=ground_stations, radio=_RADIO, traffic=_TRAFFIC,
        failures=failures or FailureConfig(),
    )


def test_zero_ground_stations_does_not_crash():
    cfg = _scenario("No stations", [])
    result = run_scenario(cfg)
    assert result.metrics["availability"] == 0.0
    assert result.metrics["max_abs_doppler_hz"] == 0.0
    assert result.metrics["command_completion_rate"] == 0.0
    assert result.metrics["commands_total"] > 0  # commands still get created and expire


def test_single_station_outed_for_entire_run_does_not_crash():
    cfg = _scenario(
        "Total outage",
        [_STATION],
        failures=FailureConfig(station_outages={"Solo": [[0, 3600]]}),
    )
    result = run_scenario(cfg)
    assert result.metrics["availability"] == 0.0
    assert result.metrics["max_abs_doppler_hz"] == 0.0


def test_station_ablation_to_zero_coverage_does_not_crash():
    """This is the scenario most likely to hit the empty-contact edge case
    in practice: the leave-one-station-out trade study removing the only
    station with any visibility in a given window."""
    cfg = _scenario("Ablation edge case", [_STATION], duration_s=1800, time_step_s=10)
    result = station_ablation(cfg)
    assert "baseline" in result
    assert len(result["cases"]) == 1
    assert result["cases"][0]["removed_station"] == "Solo"


def test_duration_shorter_than_time_step_does_not_crash():
    cfg = _scenario("Sub-step duration", [_STATION], duration_s=5, time_step_s=20)
    result = run_scenario(cfg)
    assert result.metrics["commands_total"] >= 1
    assert result.metrics["contact_time_s"] <= cfg.duration_s


def test_command_interval_longer_than_duration_still_creates_one_command():
    cfg = ScenarioConfig(
        name="Long interval", duration_s=60, time_step_s=10, orbit=_ORBIT,
        ground_stations=[_STATION], radio=_RADIO,
        traffic=TrafficConfig(
            command_interval_s=10_000, command_size_bits=2048,
            telemetry_interval_s=10_000, telemetry_size_bits=8192,
        ),
    )
    result = run_scenario(cfg)
    assert result.metrics["commands_total"] == 1
