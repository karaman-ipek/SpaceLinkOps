"""Synthetic spacecraft telemetry and robust anomaly detection."""
import numpy as np

CHANNELS=("battery_v","bus_current_a","temperature_c","attitude_error_deg")
def generate_telemetry(times_s:np.ndarray,seed:int=42)->list[dict]:
    rng=np.random.default_rng(seed); phase=2*np.pi*times_s/5700.0
    v={"battery_v":27.8+.9*np.sin(phase)+rng.normal(0,.08,len(times_s)),"bus_current_a":4.2-.5*np.sin(phase)+rng.normal(0,.12,len(times_s)),"temperature_c":19+8*np.sin(phase-.4)+rng.normal(0,.35,len(times_s)),"attitude_error_deg":np.abs(rng.normal(.08,.03,len(times_s)))}
    if len(times_s)>30: v["temperature_c"][len(times_s)//3]+=18; v["attitude_error_deg"][2*len(times_s)//3]+=1.2
    return detect_anomalies([{"time_s":float(t),**{c:float(v[c][i]) for c in CHANNELS}} for i,t in enumerate(times_s)])
def detect_anomalies(rows:list[dict],threshold:float=6.0)->list[dict]:
    if not rows:return rows
    x=np.array([[r[c] for c in CHANNELS] for r in rows]); med=np.median(x,axis=0); mad=np.median(np.abs(x-med),axis=0); z=.6745*np.abs(x-med)/np.where(mad<1e-12,1,mad)
    for row,s in zip(rows,z):
        i=int(np.argmax(s)); row.update(anomaly_score=float(s[i]),anomaly=bool(s[i]>=threshold),anomaly_channel=CHANNELS[i] if s[i]>=threshold else None)
    return rows
