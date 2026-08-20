"""Automated ground-segment trade and ablation studies."""
from .engine import run_scenario


def station_ablation(config):
    baseline=run_scenario(config).metrics;rows=[]
    for station in config.ground_stations:
        remaining=[s for s in config.ground_stations if s.name!=station.name]
        case=config.model_copy(update={"ground_stations":remaining});metrics=run_scenario(case).metrics
        rows.append({"removed_station":station.name,"availability":metrics["availability"],"command_completion_rate":metrics["command_completion_rate"],"availability_delta":metrics["availability"]-baseline["availability"],"command_delta":metrics["command_completion_rate"]-baseline["command_completion_rate"]})
    return {"baseline":baseline,"cases":rows}
