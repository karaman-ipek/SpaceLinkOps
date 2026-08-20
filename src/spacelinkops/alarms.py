"""Operational telemetry quality, stale-data and persistent limit monitoring."""
from dataclasses import dataclass


@dataclass
class LimitDefinition:name:str;yellow_low:float|None=None;yellow_high:float|None=None;red_low:float|None=None;red_high:float|None=None;debounce_samples:int=2;stale_after_s:float=120
class AlarmMonitor:
    def __init__(self,limits):self.limits={x.name:x for x in limits};self.counts={};self.active={};self.last_time={}
    def ingest(self,name,value,time_s,valid=True):
        if name not in self.limits:raise ValueError("unknown telemetry parameter")
        d=self.limits[name];self.last_time[name]=time_s
        if not valid:return {"parameter":name,"severity":"INVALID","active":True,"time_s":time_s}
        severity="NORMAL"
        if (d.red_low is not None and value<d.red_low) or (d.red_high is not None and value>d.red_high):severity="RED"
        elif (d.yellow_low is not None and value<d.yellow_low) or (d.yellow_high is not None and value>d.yellow_high):severity="YELLOW"
        key=(name,severity);self.counts[key]=self.counts.get(key,0)+1 if severity!="NORMAL" else 0
        active=severity!="NORMAL" and self.counts[key]>=d.debounce_samples
        if active:self.active[name]={"parameter":name,"severity":severity,"active":True,"value":value,"time_s":time_s,"acknowledged":False}
        elif severity=="NORMAL":self.active.pop(name,None)
        return self.active.get(name,{"parameter":name,"severity":severity,"active":False,"value":value,"time_s":time_s})
    def stale(self,now_s):return [{"parameter":n,"severity":"STALE","active":True,"age_s":now_s-t} for n,t in self.last_time.items() if now_s-t>self.limits[n].stale_after_s]
    def acknowledge(self,name,actor):
        if name not in self.active:raise ValueError("alarm is not active")
        self.active[name]["acknowledged"]=True;self.active[name]["acknowledged_by"]=actor;return dict(self.active[name])
