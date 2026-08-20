"""Dependency-graph resilience and FMEA analysis."""
from collections import deque


def build_network(stations):
    g={"Mission Control":["Terrestrial Network"],"Terrestrial Network":stations,"Spacecraft":[]}; g.update({s:["Spacecraft"] for s in stations}); return g
def _reachable(g,removed=None):
    q=deque(["Mission Control"]); seen=set()
    while q:
        n=q.popleft()
        if n==removed or n in seen:continue
        seen.add(n); q.extend(g.get(n,[]))
    return "Spacecraft" in seen
def criticality(g):return [{"component":n,"single_point_of_failure":not _reachable(g,n),"criticality":"critical" if not _reachable(g,n) else "redundant"} for n in g if n not in {"Mission Control","Spacecraft"}]
def fmea(stations):
    m=[("Terrestrial Network","Backhaul unavailable",9,3,4,"Independent routed backup"),("Spacecraft radio","Transceiver unavailable",10,2,7,"Cross-strapped transceiver"),("Mission scheduler","Commands miss access window",7,4,3,"Conflict-aware replanning")]+[(s,"Ground station outage",6,4,2,"Route traffic to another station") for s in stations]
    return [{"component":c,"failure_mode":x,"severity":s,"occurrence":o,"detectability":d,"rpn":s*o*d,"mitigation":mit} for c,x,s,o,d,mit in m]
