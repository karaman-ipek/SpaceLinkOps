from __future__ import annotations

import argparse
import json

from .config import load_scenario
from .engine import monte_carlo, run_scenario
from .trades import station_ablation


def main() -> None:
    parser=argparse.ArgumentParser(description="SpaceLinkOps TT&C simulator")
    parser.add_argument("scenario", help="YAML scenario path")
    parser.add_argument("--output", default="outputs/result.json")
    parser.add_argument("--monte-carlo", type=int, default=0, metavar="RUNS")
    parser.add_argument("--station-ablation", action="store_true")
    args=parser.parse_args(); cfg=load_scenario(args.scenario); result=run_scenario(cfg)
    path=result.save(args.output)
    print(json.dumps(result.metrics,indent=2)); print(f"Saved {path}")
    if args.monte_carlo: print(json.dumps(monte_carlo(cfg,args.monte_carlo),indent=2))
    if args.station_ablation: print(json.dumps(station_ablation(cfg),indent=2))

if __name__ == "__main__": main()
