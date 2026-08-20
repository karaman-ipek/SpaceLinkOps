from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator


class OrbitConfig(BaseModel):
    model: str = "two_body"
    altitude_km: float | None = Field(default=None, gt=100, lt=50000)
    inclination_deg: float | None = Field(default=None, ge=0, le=180)
    raan_deg: float = 0.0
    argument_of_perigee_deg: float = 0.0
    mean_anomaly_deg: float = 0.0
    tle_line1: str | None = None
    tle_line2: str | None = None

    @model_validator(mode="after")
    def valid_propagator(self):
        if self.model == "sgp4" and not (self.tle_line1 and self.tle_line2): raise ValueError("SGP4 requires both TLE lines")
        if self.model == "two_body" and (self.altitude_km is None or self.inclination_deg is None): raise ValueError("two_body requires altitude_km and inclination_deg")
        if self.model not in {"two_body","sgp4"}: raise ValueError("unknown orbit model")
        return self

class GroundStation(BaseModel):
    name: str
    latitude_deg: float = Field(ge=-90, le=90)
    longitude_deg: float = Field(ge=-180, le=180)
    elevation_mask_deg: float = Field(default=10, ge=0, lt=90)
    antenna_gain_dbi: float = 35.0
    system_noise_temperature_k: float = Field(default=500, gt=0)

class RadioConfig(BaseModel):
    frequency_hz: float = Field(gt=0)
    transmit_power_w: float = Field(gt=0)
    spacecraft_antenna_gain_dbi: float
    system_losses_db: float = Field(default=3, ge=0)
    atmospheric_loss_db: float = Field(default=1, ge=0)
    bandwidth_hz: float = Field(gt=0)
    data_rate_bps: float = Field(gt=0)
    required_ebn0_db: float = 6.0

class TrafficConfig(BaseModel):
    command_interval_s: float = Field(gt=0)
    command_size_bits: int = Field(gt=0)
    telemetry_interval_s: float = Field(gt=0)
    telemetry_size_bits: int = Field(gt=0)
    max_retries: int = Field(default=2, ge=0, le=20)
    processing_delay_s: float = Field(default=0.15, ge=0)
    command_ttl_s: float = Field(default=1800, gt=0)

class FailureConfig(BaseModel):
    station_outages: dict[str, list[list[float]]] = {}
    network_delay_windows: list[list[float]] = []
    network_extra_delay_s: float = Field(default=0, ge=0)
    link_margin_penalty_db: float = Field(default=0, ge=0)
    margin_jitter_sigma_db: float = Field(default=1.5, ge=0)
    packet_corruption_probability: float = Field(default=0.002, ge=0, le=1)

class ScenarioConfig(BaseModel):
    name: str
    duration_s: int = Field(gt=0)
    time_step_s: int = Field(default=10, gt=0)
    seed: int = 42
    orbit: OrbitConfig
    ground_stations: list[GroundStation]
    radio: RadioConfig
    traffic: TrafficConfig
    failures: FailureConfig = FailureConfig()

    @model_validator(mode="after")
    def station_names_unique(self):
        names = [s.name for s in self.ground_stations]
        if len(names) != len(set(names)):
            raise ValueError("Ground-station names must be unique")
        unknown = set(self.failures.station_outages) - set(names)
        if unknown:
            raise ValueError(f"Outages reference unknown stations: {sorted(unknown)}")
        return self

def load_scenario(path: str | Path) -> ScenarioConfig:
    with Path(path).open(encoding="utf-8") as handle:
        return ScenarioConfig.model_validate(yaml.safe_load(handle))
