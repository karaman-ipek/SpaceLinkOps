"""Property-based tests for the RF link budget.

These generate many random-but-valid inputs (matching the pydantic field
constraints in config.py) and assert the link math never raises and always
returns values in a physically sane range, rather than checking one or two
hand-picked numbers.
"""
import math

from hypothesis import given, settings
from hypothesis import strategies as st

from spacelinkops.config import GroundStation, RadioConfig
from spacelinkops.link import free_space_path_loss_db, link_metrics, packet_success_probability

# Bounds mirror the Field(...) constraints in config.py so generated cases
# are always valid, realistic inputs rather than nonsense the model would
# already reject at load time.
_range_m = st.floats(min_value=1.0, max_value=5e7, allow_nan=False, allow_infinity=False)
_freq_hz = st.floats(min_value=1e6, max_value=4e10, allow_nan=False, allow_infinity=False)
_margin_db = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)


@given(_range_m, _freq_hz)
@settings(max_examples=200)
def test_fspl_never_raises_and_is_finite(range_m, frequency_hz):
    value = free_space_path_loss_db(range_m, frequency_hz)
    assert math.isfinite(value)


@given(st.one_of(st.just(0.0), st.floats(max_value=0.0)), _freq_hz)
def test_fspl_rejects_non_positive_range(range_m, frequency_hz):
    try:
        free_space_path_loss_db(range_m, frequency_hz)
    except ValueError:
        return
    assert False, "expected ValueError for non-positive range"


@given(_margin_db)
@settings(max_examples=200)
def test_packet_success_probability_always_in_unit_interval(margin_db):
    p = packet_success_probability(margin_db)
    assert 0.0 <= p <= 1.0


@given(
    range_m=_range_m,
    frequency_hz=st.floats(min_value=1e8, max_value=4e10, allow_nan=False, allow_infinity=False),
    transmit_power_w=st.floats(min_value=0.01, max_value=1000, allow_nan=False, allow_infinity=False),
    spacecraft_gain_dbi=st.floats(min_value=-20, max_value=40, allow_nan=False, allow_infinity=False),
    station_gain_dbi=st.floats(min_value=0, max_value=70, allow_nan=False, allow_infinity=False),
    noise_temp_k=st.floats(min_value=1, max_value=5000, allow_nan=False, allow_infinity=False),
    bandwidth_hz=st.floats(min_value=1, max_value=1e9, allow_nan=False, allow_infinity=False),
    data_rate_bps=st.floats(min_value=1, max_value=1e9, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_link_metrics_never_raises_for_valid_config(
    range_m, frequency_hz, transmit_power_w, spacecraft_gain_dbi,
    station_gain_dbi, noise_temp_k, bandwidth_hz, data_rate_bps,
):
    station = GroundStation(
        name="Fuzz", latitude_deg=0, longitude_deg=0,
        antenna_gain_dbi=station_gain_dbi, system_noise_temperature_k=noise_temp_k,
    )
    radio = RadioConfig(
        frequency_hz=frequency_hz, transmit_power_w=transmit_power_w,
        spacecraft_antenna_gain_dbi=spacecraft_gain_dbi,
        bandwidth_hz=bandwidth_hz, data_rate_bps=data_rate_bps,
    )
    metrics = link_metrics(range_m, station, radio)
    for key, value in metrics.items():
        assert math.isfinite(value), f"{key} is not finite"
