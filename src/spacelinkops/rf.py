"""Modulation-specific uncoded AWGN BER/PER and Doppler."""
import math

from .constants import SPEED_OF_LIGHT_M_S


def ber_awgn(ebn0_db,modulation="BPSK"):
    if modulation.upper() not in {"BPSK","QPSK"}:raise ValueError("Supported: BPSK, QPSK")
    return .5*math.erfc(math.sqrt(10**(ebn0_db/10)))
def packet_error_rate(ebn0_db,bits,modulation="BPSK"):
    if bits<=0:raise ValueError("bits must be positive")
    ber=ber_awgn(ebn0_db,modulation);return 1-math.exp(bits*math.log1p(-ber))
def doppler_shift_hz(range_rate_m_s,carrier_hz):return -range_rate_m_s*carrier_hz/SPEED_OF_LIGHT_M_S
