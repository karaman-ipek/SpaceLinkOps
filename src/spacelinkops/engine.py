import json
from dataclasses import asdict, dataclass
from itertools import pairwise
from pathlib import Path

import numpy as np

from .config import ScenarioConfig
from .constants import EARTH_RADIUS_M, SPEED_OF_LIGHT_M_S
from .link import link_metrics
from .network import build_network, criticality, fmea
from .orbit import contact_windows, geometry, satellite_ecef
from .rf import doppler_shift_hz, packet_error_rate
from .scheduler import Command, choose_station
from .telemetry import generate_telemetry


@dataclass
class Event:
    time_s:float; kind:str; station:str|None; success:bool; latency_s:float|None; margin_db:float|None; attempts:int=1
@dataclass
class SimulationResult:
    scenario:str; metrics:dict; contacts:dict; events:list[Event]; timeline:list[dict]; risks:list[dict]; commands:list[dict]; telemetry:list[dict]; network:dict
    def to_dict(self):return {"scenario":self.scenario,"metrics":self.metrics,"contacts":self.contacts,"events":[asdict(e) for e in self.events],"timeline":self.timeline,"risks":self.risks,"commands":self.commands,"telemetry":self.telemetry,"network":self.network}
    def save(self,path):
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(self.to_dict(),indent=2),encoding="utf-8");return p

def _inside(t,w):return any(a<=t<=b for a,b in w)
def _candidates(cfg,t,jitter=0.0):
    out=[]
    for s in cfg.ground_stations:
        if _inside(t,cfg.failures.station_outages.get(s.name,[])):continue
        elev,distance=geometry(cfg.orbit,s,t)
        if elev>=s.elevation_mask_deg:
            lm=link_metrics(distance,s,cfg.radio,cfg.failures.link_margin_penalty_db-jitter);out.append((lm["link_margin_db"],s,distance,elev,lm))
    return out
def _packet(cfg,rng,best,t,kind,size):
    margin,s,distance,_,lm=best
    physical_success=1-packet_error_rate(lm["ebn0_db"],size,"BPSK")
    p=physical_success*(1-cfg.failures.packet_corruption_probability);success=False
    for attempts in range(1,cfg.traffic.max_retries+2):
        if rng.random()<p:success=True;break
    extra=cfg.failures.network_extra_delay_s if _inside(t,cfg.failures.network_delay_windows) else 0
    latency=(2 if kind=="command" else 1)*distance/SPEED_OF_LIGHT_M_S+size/cfg.radio.data_rate_bps+cfg.traffic.processing_delay_s+extra
    return Event(t,kind,s.name,success,latency if success else None,margin,attempts)

def run_scenario(cfg:ScenarioConfig)->SimulationResult:
    rng=np.random.default_rng(cfg.seed);events=[];commands=[];timeline=[]
    contacts={s.name:contact_windows(cfg.orbit,s,cfg.duration_s,cfg.time_step_s) for s in cfg.ground_stations}
    for t in range(0,cfg.duration_s+1,cfg.time_step_s):
        best=choose_station(_candidates(cfg,t,float(rng.normal(0,cfg.failures.margin_jitter_sigma_db))));p=satellite_ecef(cfg.orbit,t)/EARTH_RADIUS_M
        range_rate=None;doppler=None
        if best:
            _,d2=geometry(cfg.orbit,best[1],t+1);range_rate=d2-best[2];doppler=doppler_shift_hz(range_rate,cfg.radio.frequency_hz)
        timeline.append({"time_s":t,"station":best[1].name if best else None,"elevation_deg":best[3] if best else None,"range_km":best[2]/1000 if best else None,"link_margin_db":best[0] if best else None,"range_rate_m_s":range_rate,"doppler_hz":doppler,"x_er":float(p[0]),"y_er":float(p[1]),"z_er":float(p[2])})
    pending=[];times=np.arange(0,cfg.duration_s+1e-9,cfg.traffic.command_interval_s);i=0
    for t in range(0,cfg.duration_s+1,cfg.time_step_s):
        while i<len(times) and times[i]<=t:
            c=Command(f"CMD-{i+1:04d}",float(times[i]),cfg.traffic.command_ttl_s,1,cfg.traffic.command_size_bits);c.transition("CREATED",c.created_s);c.transition("QUEUED",c.created_s);pending.append(c);i+=1
        for c in list(pending):
            if t-c.created_s>c.ttl_s:c.transition("EXPIRED",t,"No access before TTL");commands.append(c.to_dict());pending.remove(c)
        best=choose_station(_candidates(cfg,t,float(rng.normal(0,cfg.failures.margin_jitter_sigma_db))))
        if best and pending:
            c=pending.pop(0);c.station=best[1].name;c.transition("UPLINKED",t,c.station);e=_packet(cfg,rng,best,t,"command",c.size_bits);events.append(e)
            if e.success:c.transition("RECEIVED",t+e.latency_s/2);c.transition("EXECUTED",t+e.latency_s/2+cfg.traffic.processing_delay_s);c.transition("ACKNOWLEDGED",t+e.latency_s)
            else:c.transition("FAILED",t,"Retry budget exhausted")
            commands.append(c.to_dict())
    for c in pending:c.transition("EXPIRED",cfg.duration_s,"Simulation ended");commands.append(c.to_dict())
    tel_times=np.arange(0,cfg.duration_s+1e-9,cfg.traffic.telemetry_interval_s)
    for t_val in tel_times:
        t_seconds=float(t_val)
        best=choose_station(_candidates(cfg,t_seconds,float(rng.normal(0,cfg.failures.margin_jitter_sigma_db))))
        events.append(_packet(cfg,rng,best,t_seconds,"telemetry",cfg.traffic.telemetry_size_bits) if best else Event(t_seconds,"telemetry",None,False,None,None,0))
    delivered=[e for e in events if e.success];attempted=[e for e in events if e.attempts>0];lat=[e.latency_s for e in delivered]
    visible=sum(x["station"] is not None for x in timeline)*cfg.time_step_s;completed=sum(c["state"]=="ACKNOWLEDGED" for c in commands)
    telemetry=generate_telemetry(tel_times,cfg.seed);stations=[s.name for s in cfg.ground_stations];graph=build_network(stations);network={"graph":graph,"criticality":criticality(graph),"fmea":fmea(stations)}
    access_sequence=[x["station"] for x in timeline if x["station"]]
    switches=sum(a!=b for a,b in pairwise(access_sequence))
    metrics={"commands_total":len(commands),"commands_acknowledged":completed,"command_completion_rate":completed/len(commands),"telemetry_delivery_rate":sum(e.success for e in events if e.kind=="telemetry")/len(tel_times),"in_contact_success_rate":len(delivered)/len(attempted) if attempted else 0,"mean_latency_s":float(np.mean(lat)) if lat else None,"p95_latency_s":float(np.percentile(lat,95)) if lat else None,"contact_time_s":min(visible,cfg.duration_s),"availability":min(visible,cfg.duration_s)/cfg.duration_s,"station_switches":switches,"max_abs_doppler_hz":max((abs(x["doppler_hz"]) for x in timeline if x["doppler_hz"] is not None), default=0.0),"anomalies_detected":sum(r["anomaly"] for r in telemetry)}
    return SimulationResult(cfg.name,metrics,contacts,events,timeline,_risks(metrics,network),commands,telemetry,network)
def _risks(m,n):
    r=[]
    if m["availability"]<.1:r.append({"severity":"high","issue":"Low ground-segment coverage","evidence":f'{m["availability"]:.1%} availability',"mitigation":"Add stations or optimize sites."})
    if m["command_completion_rate"]<.95:r.append({"severity":"high","issue":"Command completion below objective","evidence":f'{m["command_completion_rate"]:.1%} acknowledged',"mitigation":"Increase TTL, coverage, or link robustness."})
    for x in n["criticality"]:
        if x["single_point_of_failure"]:r.append({"severity":"critical","issue":f'{x["component"]} is a single point of failure',"evidence":"Graph cut disconnects control from spacecraft","mitigation":"Add an independent path."})
    return r
def monte_carlo(cfg,runs=100):
    v=[run_scenario(cfg.model_copy(update={"seed":s})).metrics["command_completion_rate"] for s in range(cfg.seed,cfg.seed+runs)]
    return {"runs":runs,"mean_command_completion_rate":float(np.mean(v)),"std":float(np.std(v)),"p05":float(np.percentile(v,5)),"p50":float(np.percentile(v,50)),"p95":float(np.percentile(v,95)),"samples":v}
