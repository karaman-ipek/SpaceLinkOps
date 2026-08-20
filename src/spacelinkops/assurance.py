"""Tamper-evident audit evidence for the offline operations demonstrator."""
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class AuditRecord:
    sequence:int;timestamp_utc:str;actor:str;action:str;object_id:str;details:dict;previous_hash:str;record_hash:str
class AuditLog:
    def __init__(self):self._records=[]
    def append(self,actor,action,object_id,details=None,timestamp=None):
        previous=self._records[-1].record_hash if self._records else "GENESIS";stamp=timestamp or datetime.now(UTC).isoformat()
        body={"sequence":len(self._records),"timestamp_utc":stamp,"actor":actor,"action":action,"object_id":object_id,"details":details or {},"previous_hash":previous}
        digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest();record=AuditRecord(**body,record_hash=digest);self._records.append(record);return record
    def verify(self):
        previous="GENESIS"
        for record in self._records:
            body=asdict(record);digest=body.pop("record_hash")
            if body["previous_hash"]!=previous or hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=digest:return False
            previous=digest
        return True
    def export(self):return [asdict(r) for r in self._records]
