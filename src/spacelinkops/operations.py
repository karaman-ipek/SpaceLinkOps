"""Offline command authority with RBAC, dual control, interlocks and inhibit."""
from dataclasses import asdict, dataclass, field
from enum import Enum

from .assurance import AuditLog


class Role(str,Enum):OPERATOR="operator";APPROVER="approver";FLIGHT_DIRECTOR="flight_director";OBSERVER="observer"
@dataclass(frozen=True)
class User:username:str;role:Role
@dataclass(frozen=True)
class CommandDefinition:
    name:str;hazardous:bool=False;allowed_modes:tuple[str,...]=("NOMINAL",);parameters:dict[str,tuple[float,float]]=field(default_factory=dict)
@dataclass
class OperationalCommand:
    command_id:str;definition:str;parameters:dict;submitter:str;state:str="DRAFT";approvals:list[str]=field(default_factory=list);reason:str=""
    def to_dict(self):return asdict(self)
class CommandAuthority:
    def __init__(self,definitions):self.definitions={d.name:d for d in definitions};self.commands={};self.inhibited=False;self.audit=AuditLog();self._counter=0
    def _require(self,user,*roles):
        if user.role not in roles:raise PermissionError(f"role {user.role} not authorized")
    def submit(self,user,name,parameters,spacecraft_mode):
        self._require(user,Role.OPERATOR,Role.FLIGHT_DIRECTOR)
        if self.inhibited:raise RuntimeError("command release is globally inhibited")
        if name not in self.definitions:raise ValueError("unknown command")
        d=self.definitions[name]
        if spacecraft_mode not in d.allowed_modes:raise ValueError("mode interlock rejected command")
        for key,(lo,hi) in d.parameters.items():
            if key not in parameters or not lo<=float(parameters[key])<=hi:raise ValueError(f"parameter constraint failed: {key}")
        self._counter+=1;c=OperationalCommand(f"OPCMD-{self._counter:05d}",name,parameters,user.username,"PENDING_APPROVAL");self.commands[c.command_id]=c;self.audit.append(user.username,"SUBMIT",c.command_id,c.to_dict());return c
    def approve(self,user,command_id):
        self._require(user,Role.APPROVER,Role.FLIGHT_DIRECTOR);c=self.commands[command_id]
        if user.username==c.submitter or user.username in c.approvals:raise ValueError("independent unique approval required")
        c.approvals.append(user.username);needed=2 if self.definitions[c.definition].hazardous else 1;c.state="APPROVED" if len(c.approvals)>=needed else "PENDING_APPROVAL";self.audit.append(user.username,"APPROVE",command_id,{"approval_count":len(c.approvals)});return c
    def release(self,user,command_id,spacecraft_mode):
        self._require(user,Role.FLIGHT_DIRECTOR);c=self.commands[command_id];d=self.definitions[c.definition]
        if self.inhibited:raise RuntimeError("command release is globally inhibited")
        if c.state!="APPROVED" or spacecraft_mode not in d.allowed_modes:raise RuntimeError("release interlock rejected command")
        c.state="RELEASED_TO_SIMULATOR";self.audit.append(user.username,"RELEASE",command_id,{"offline_only":True});return c
    def set_inhibit(self,user,enabled,reason):
        self._require(user,Role.FLIGHT_DIRECTOR);self.inhibited=bool(enabled);self.audit.append(user.username,"INHIBIT_ON" if enabled else "INHIBIT_OFF","GLOBAL",{"reason":reason})
