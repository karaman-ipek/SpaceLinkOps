"""Contact-aware command lifecycle."""
from dataclasses import asdict, dataclass, field

STATES=("CREATED","QUEUED","UPLINKED","RECEIVED","EXECUTED","ACKNOWLEDGED","EXPIRED","FAILED")
@dataclass
class Command:
    command_id:str; created_s:float; ttl_s:float; priority:int; size_bits:int; state:str="CREATED"; station:str|None=None; history:list[dict]=field(default_factory=list)
    def transition(self,state,time_s,detail=""):
        if state not in STATES:raise ValueError(state)
        self.state=state; self.history.append({"state":state,"time_s":float(time_s),"detail":detail})
    def to_dict(self):return asdict(self)
def choose_station(candidates):return max(candidates,key=lambda x:(x[0],x[3],x[1].name)) if candidates else None
