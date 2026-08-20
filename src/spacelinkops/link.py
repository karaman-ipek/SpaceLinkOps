from __future__ import annotations

import math

from .config import GroundStation, RadioConfig
from .constants import BOLTZMANN_DBW_K_HZ, SPEED_OF_LIGHT_M_S


def dbw(power_w: float) -> float: return 10*math.log10(power_w)

def free_space_path_loss_db(range_m: float, frequency_hz: float) -> float:
    """FSPL = 20 log10(4*pi*R*f/c), with R in m and f in Hz."""
    if range_m <= 0 or frequency_hz <= 0: raise ValueError("Range and frequency must be positive")
    return 20*math.log10(4*math.pi*range_m*frequency_hz/SPEED_OF_LIGHT_M_S)

def link_metrics(range_m: float, station: GroundStation, radio: RadioConfig, margin_penalty_db: float=0) -> dict:
    fspl = free_space_path_loss_db(range_m, radio.frequency_hz)
    received = dbw(radio.transmit_power_w)+radio.spacecraft_antenna_gain_dbi+station.antenna_gain_dbi-fspl-radio.system_losses_db-radio.atmospheric_loss_db-margin_penalty_db
    n0 = BOLTZMANN_DBW_K_HZ + 10*math.log10(station.system_noise_temperature_k)
    cn0 = received-n0
    ebn0 = cn0-10*math.log10(radio.data_rate_bps)
    margin = ebn0-radio.required_ebn0_db
    snr = cn0-10*math.log10(radio.bandwidth_hz)
    return {"fspl_db":fspl,"received_power_dbw":received,"cn0_dbhz":cn0,"ebn0_db":ebn0,"snr_db":snr,"link_margin_db":margin}

def packet_success_probability(margin_db: float) -> float:
    """Explicit logistic engineering approximation, not a modem BER model."""
    return 1/(1+math.exp(-max(-60,min(60,margin_db))/1.5))
