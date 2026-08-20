"""Compact CCSDS-inspired transfer frames with CRC-16-CCITT."""
import struct
from dataclasses import dataclass


def crc16_ccitt(data:bytes,initial:int=0xffff)->int:
    crc=initial
    for byte in data:
        crc^=byte<<8
        for _ in range(8):crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc
@dataclass(frozen=True)
class TransferFrame:
    spacecraft_id:int;virtual_channel:int;sequence:int;payload:bytes
    def encode(self):
        if not 0<=self.spacecraft_id<1024 or not 0<=self.virtual_channel<8:raise ValueError("identifier out of range")
        if len(self.payload)>0xffff:raise ValueError("payload exceeds maximum frame length")
        head=struct.pack(">HHH",(self.spacecraft_id<<3)|self.virtual_channel,self.sequence&0xffff,len(self.payload));body=head+self.payload
        return body+struct.pack(">H",crc16_ccitt(body))
    @classmethod
    def decode(cls,data):
        if len(data)<8 or crc16_ccitt(data[:-2])!=struct.unpack(">H",data[-2:])[0]:raise ValueError("frame CRC failure")
        ident,seq,n=struct.unpack(">HHH",data[:6]);payload=data[6:-2]
        if len(payload)!=n:raise ValueError("frame length mismatch")
        return cls(ident>>3,ident&7,seq,payload)
