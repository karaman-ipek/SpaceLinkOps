import math

from spacelinkops.frames import TransferFrame, crc16_ccitt
from spacelinkops.rf import ber_awgn, doppler_shift_hz, packet_error_rate


def test_crc_known_vector():assert crc16_ccitt(b"123456789")==0x29B1
def test_frame_roundtrip_and_corruption():
    frame=TransferFrame(42,3,65537,b"status=nominal");raw=frame.encode();assert TransferFrame.decode(raw)==TransferFrame(42,3,1,b"status=nominal")
    damaged=bytearray(raw);damaged[7]^=1
    try:TransferFrame.decode(bytes(damaged));assert False
    except ValueError:pass
def test_bpsk_reference_and_doppler():
    assert math.isclose(ber_awgn(0),0.0786496035,rel_tol=1e-8)
    assert packet_error_rate(8,1024)<packet_error_rate(4,1024)
    assert doppler_shift_hz(1000,2.2e9)<0
