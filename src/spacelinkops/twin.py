"""Small deterministic spacecraft digital twin with safe-mode FDIR."""
from dataclasses import asdict, dataclass


@dataclass
class SpacecraftState:
    time_s:float=0;mode:str="NOMINAL";battery_v:float=28.0;temperature_c:float=20.0;radio_healthy:bool=True;watchdog_count:int=0
class DigitalTwin:
    def __init__(self):self.state=SpacecraftState();self.events=[]
    def inject_fault(self,name):
        if name=="radio_failure":self.state.radio_healthy=False
        elif name=="battery_undervoltage":self.state.battery_v=21.0
        elif name=="thermal_runaway":self.state.temperature_c=75.0
        else:raise ValueError("unknown fault")
        self.events.append({"time_s":self.state.time_s,"event":"FAULT_INJECTED","fault":name});self._fdir()
    def step(self,dt_s):
        self.state.time_s+=dt_s;self.state.battery_v-=.00002*dt_s;self.state.temperature_c+=(-.001*(self.state.temperature_c-20))*dt_s;self.state.watchdog_count+=1;self._fdir();return asdict(self.state)
    def _fdir(self):
        causes=[]
        if self.state.battery_v<22:causes.append("UNDERVOLTAGE")
        if self.state.temperature_c>60:causes.append("OVERTEMPERATURE")
        if not self.state.radio_healthy:causes.append("RADIO_FAILURE")
        if causes and self.state.mode!="SAFE":self.state.mode="SAFE";self.events.append({"time_s":self.state.time_s,"event":"ENTER_SAFE_MODE","causes":causes})
