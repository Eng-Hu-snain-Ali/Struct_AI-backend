from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class BuildingInfo(BaseModel):
    building_name: str
    building_type: str
    construction_year: int = Field(..., le=datetime.now().year, description="Must not be in the future")
    floors: int = Field(..., gt=0)
    total_area: float = Field(..., gt=0)
    location: str

class StructuralModel(BaseModel):
    concrete_grade: str
    steel_grade: str
    crack_width: float = Field(..., gt=0)
    corrosion_level: float = Field(..., ge=0, le=100)
    reinforcement_diameter: float = Field(..., gt=0)
    water_cement_ratio: float = Field(0.5, gt=0, le=1.0)
    soil_bearing_capacity: float = Field(200.0, gt=0)
    settlement_value: float = Field(0.0, ge=0)
    groundwater_level: float = Field(5.0, ge=0)

    @field_validator("concrete_grade")
    @classmethod
    def validate_concrete_grade(cls, value: str) -> str:
        match = re.search(r"\d+(\.\d+)?", value or "")
        if not match:
            raise ValueError("concrete_grade must contain a positive numeric grade")
        if float(match.group()) <= 0:
            raise ValueError("concrete_grade must be > 0")
        return value

class EnvironmentalModel(BaseModel):
    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0)
    pollution_level: str
    coastal_exposure: bool
    moisture_sensor_baseline: float = Field(40.0, ge=0, le=100)

class LoadModel(BaseModel):
    dead_load: float = Field(..., gt=0)
    live_load: float = Field(..., gt=0)
    wind_load: float = Field(..., ge=0)
    seismic_load: float = Field(..., ge=0)
    vibration_load: float = Field(..., ge=0)

class EngineeringInput(BaseModel):
    building_info: BuildingInfo
    structural_model: StructuralModel
    environmental_model: EnvironmentalModel
    load_model: LoadModel

class SensorInput(BaseModel):
    building_id: int
    crack_sensor: float = Field(..., ge=0)
    vibration_sensor: float = Field(..., ge=0)
    tilt_sensor: float
    moisture_sensor: float = Field(..., ge=0, le=100)
    corrosion_sensor: float = Field(..., ge=0, le=100)
