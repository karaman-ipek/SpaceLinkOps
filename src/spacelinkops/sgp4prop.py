"""SGP4/TLE adapter and approximate TEME-to-ECEF rotation."""
import math

import numpy as np
from sgp4.api import Satrec


def _gmst(jd):
    t=(jd-2451545.0)/36525;return math.radians((280.46061837+360.98564736629*(jd-2451545)+.000387933*t*t-t*t*t/38710000)%360)
def propagate_ecef(line1,line2,time_s):
    sat=Satrec.twoline2rv(line1,line2);jd=sat.jdsatepoch+sat.jdsatepochF+time_s/86400;whole=math.floor(jd);err,r,v=sat.sgp4(whole,jd-whole)
    if err:raise RuntimeError(f"SGP4 error {err}")
    a=_gmst(jd);c,s=math.cos(a),math.sin(a);rot=np.array([[c,s,0],[-s,c,0],[0,0,1]])
    position=rot@np.array(r)*1000;velocity=rot@np.array(v)*1000-np.cross(np.array([0,0,7.2921150e-5]),position)
    return position,velocity
