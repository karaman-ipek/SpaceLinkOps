import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from spacelinkops import load_scenario, run_scenario
from spacelinkops.engine import monte_carlo
from spacelinkops.operations import CommandAuthority, CommandDefinition, Role, User
from spacelinkops.trades import station_ablation

st.set_page_config(page_title="SpaceLinkOps",page_icon="🛰️",layout="wide")
st.markdown("# 🛰️ SpaceLinkOps · Mission Resilience Lab")
scenario=st.sidebar.selectbox("Mission scenario",sorted(Path("scenarios").glob("*.yaml")),format_func=lambda p:p.stem);runs=st.sidebar.slider("Monte Carlo runs",20,300,100,20)
cfg=load_scenario(scenario);r=run_scenario(cfg);m=r.metrics
cards=[("Commands ACK",f'{m["command_completion_rate"]:.1%}'),("Telemetry",f'{m["telemetry_delivery_rate"]:.1%}'),("Availability",f'{m["availability"]:.1%}'),("P95 latency",f'{m["p95_latency_s"] or 0:.3f}s'),("Anomalies",m["anomalies_detected"]),("Critical risks",sum(x["severity"]=="critical" for x in r.risks))]
for col,(k,v) in zip(st.columns(6),cards):col.metric(k,v)
tabs=st.tabs(["3D Orbit","RF & Access","Command Lifecycle","Telemetry AI","Resilience","Monte Carlo","Ops Assurance"]);df=pd.DataFrame(r.timeline)
with tabs[0]:
    u=np.linspace(0,2*np.pi,40);v=np.linspace(0,np.pi,20);x=np.outer(np.cos(u),np.sin(v));y=np.outer(np.sin(u),np.sin(v));z=np.outer(np.ones_like(u),np.cos(v))
    fig=go.Figure(go.Surface(x=x,y=y,z=z,colorscale="Blues",showscale=False,opacity=.75));fig.add_trace(go.Scatter3d(x=df.x_er,y=df.y_er,z=df.z_er,mode="lines",line={"color":"#ffb000","width":4},name="Orbit"))
    for s in cfg.ground_stations:
        lat,lon=np.radians([s.latitude_deg,s.longitude_deg]);fig.add_trace(go.Scatter3d(x=[np.cos(lat)*np.cos(lon)],y=[np.cos(lat)*np.sin(lon)],z=[np.sin(lat)],mode="markers+text",text=[s.name],marker={"size":5,"color":"#00ffcc"},name=s.name))
    fig.update_layout(template="plotly_dark",height=680,scene={"aspectmode":"data","xaxis_visible":False,"yaxis_visible":False,"zaxis_visible":False},margin={"l":0,"r":0,"t":0,"b":0});st.plotly_chart(fig,width="stretch")
with tabs[1]:
    st.plotly_chart(px.line(df,x="time_s",y="elevation_deg",color="station",title="Selected-station elevation"),width="stretch");st.plotly_chart(px.line(df,x="time_s",y="link_margin_db",color="station",title="Dynamic link margin with stochastic fading"),width="stretch");st.plotly_chart(px.line(df,x="time_s",y="doppler_hz",color="station",title="Predicted carrier Doppler"),width="stretch")
with tabs[2]:
    cmd=pd.DataFrame(r.commands)
    if cmd.empty:
        st.info("No commands were generated for this scenario.")
    else:
        st.plotly_chart(px.histogram(cmd,x="state",color="state",title="Final command states"),width="stretch");chosen=st.selectbox("Inspect command",cmd.command_id);st.dataframe(pd.DataFrame(cmd.loc[cmd.command_id==chosen,"history"].iloc[0]),width="stretch")
with tabs[3]:
    tel=pd.DataFrame(r.telemetry);channel=st.selectbox("Telemetry channel",["battery_v","bus_current_a","temperature_c","attitude_error_deg"]);fig=px.line(tel,x="time_s",y=channel,title=f"{channel} · robust MAD anomaly detection");bad=tel[tel.anomaly];fig.add_scatter(x=bad.time_s,y=bad[channel],mode="markers",marker={"color":"red","size":10,"symbol":"x"},name="Anomaly");st.plotly_chart(fig,width="stretch")
with tabs[4]:
    st.subheader("Automated risk register");st.dataframe(r.risks,width="stretch");st.subheader("Failure Mode and Effects Analysis");st.dataframe(sorted(r.network["fmea"],key=lambda x:x["rpn"],reverse=True),width="stretch");st.subheader("Graph-cut criticality");st.dataframe(r.network["criticality"],width="stretch")
    if st.button("Run station ablation trade study"):
        trade=station_ablation(cfg);st.dataframe(trade["cases"],width="stretch")
with tabs[5]:
    if st.button("Run resilience ensemble"):
        mc=monte_carlo(cfg,runs);st.json({k:v for k,v in mc.items() if k!="samples"});st.plotly_chart(px.histogram(x=mc["samples"],nbins=20,title="Command completion distribution"),width="stretch")
with tabs[6]:
    st.warning("OFFLINE DEMONSTRATOR — no real spacecraft or ground-equipment interface exists")
    authority=CommandAuthority([CommandDefinition("SET_HEATER",False,("NOMINAL",),{"level":(0,100)})]);op=User("operator-1",Role.OPERATOR);approver=User("controller-2",Role.APPROVER);director=User("flight-director",Role.FLIGHT_DIRECTOR)
    command=authority.submit(op,"SET_HEATER",{"level":25},"NOMINAL");authority.approve(approver,command.command_id);authority.release(director,command.command_id,"NOMINAL")
    st.subheader("Dual-control command gate demonstration");st.json(command.to_dict());st.subheader("Tamper-evident audit chain");st.dataframe(authority.audit.export(),width="stretch");st.success(f"Audit chain verification: {authority.audit.verify()}")
