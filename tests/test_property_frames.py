"""Property-based tests for TransferFrame encode/decode."""
from hypothesis import given, settings
from hypothesis import strategies as st

from spacelinkops.frames import TransferFrame

_spacecraft_id = st.integers(min_value=0, max_value=1023)
_virtual_channel = st.integers(min_value=0, max_value=7)
_sequence = st.integers(min_value=0, max_value=2**32 - 1)
_payload = st.binary(min_size=0, max_size=2048)


@given(_spacecraft_id, _virtual_channel, _sequence, _payload)
@settings(max_examples=300)
def test_encode_decode_roundtrip(spacecraft_id, virtual_channel, sequence, payload):
    frame = TransferFrame(spacecraft_id, virtual_channel, sequence, payload)
    decoded = TransferFrame.decode(frame.encode())
    assert decoded.spacecraft_id == spacecraft_id
    assert decoded.virtual_channel == virtual_channel
    assert decoded.sequence == sequence & 0xFFFF  # sequence field is 16 bits on the wire
    assert decoded.payload == payload


@given(_payload)
@settings(max_examples=50)
def test_out_of_range_identifiers_rejected(payload):
    for bad in (TransferFrame(1024, 0, 0, payload), TransferFrame(0, 8, 0, payload), TransferFrame(-1, 0, 0, payload)):
        try:
            bad.encode()
        except ValueError:
            continue
        assert False, "expected ValueError for out-of-range identifier"


def test_oversized_payload_rejected():
    frame = TransferFrame(1, 0, 0, b"x" * 65536)
    try:
        frame.encode()
    except ValueError:
        return
    assert False, "expected ValueError for payload exceeding 65535 bytes"


@given(_spacecraft_id, _virtual_channel, _sequence, st.binary(min_size=1, max_size=256), st.integers(min_value=0, max_value=255))
@settings(max_examples=200)
def test_single_bit_corruption_detected(spacecraft_id, virtual_channel, sequence, payload, corrupt_index):
    raw = bytearray(TransferFrame(spacecraft_id, virtual_channel, sequence, payload).encode())
    index = corrupt_index % len(raw)
    raw[index] ^= 0x01
    try:
        TransferFrame.decode(bytes(raw))
    except ValueError:
        return
    assert False, "expected CRC failure to be detected"
