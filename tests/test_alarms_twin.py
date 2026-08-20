from spacelinkops.alarms import AlarmMonitor, LimitDefinition
from spacelinkops.twin import DigitalTwin


def test_alarm_debounce_and_acknowledgement():
    m=AlarmMonitor([LimitDefinition("temp",yellow_high=40,red_high=60,debounce_samples=2)]);assert not m.ingest("temp",70,0)["active"];assert m.ingest("temp",70,1)["active"];assert m.acknowledge("temp","operator")["acknowledged"]
def test_stale_detection():
    m=AlarmMonitor([LimitDefinition("battery",stale_after_s=10)]);m.ingest("battery",28,0);assert m.stale(11)[0]["severity"]=="STALE"
def test_critical_fault_enters_safe_mode():
    twin=DigitalTwin();twin.inject_fault("battery_undervoltage");assert twin.state.mode=="SAFE" and twin.events[-1]["event"]=="ENTER_SAFE_MODE"
