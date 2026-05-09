from app.schemas.building import EngineeringInput
from datetime import datetime
import math

def calculate_concrete_durability_factor(concrete_grade: str, age_years: int, crack_width: float, water_cement_ratio: float) -> float:
    base_strength = float(''.join(filter(str.isdigit, concrete_grade)) or 30)
    wcr_penalty = max((water_cement_ratio - 0.4) * 0.5, 0)
    crack_penalty = min(crack_width * 0.15, 0.5)
    age_penalty = min(age_years * 0.005, 0.4)
    
    durability = base_strength * (1 - wcr_penalty - crack_penalty - age_penalty)
    return max(durability, 0.0)

def calculate_corrosion_rate_multiplier(corrosion_level: float, coastal_exposure: bool, humidity: float, moisture_sensor: float) -> float:
    base_rate = max(corrosion_level, 0.1)
    environmental_factor = 1.5 if coastal_exposure else 1.0
    
    # Exponential increase based on humidity and moisture
    humidity_factor = math.exp(max(humidity - 50, 0) * 0.02)
    moisture_factor = math.exp(max(moisture_sensor - 30, 0) * 0.03)
    
    rate = base_rate * environmental_factor * humidity_factor * moisture_factor
    return min(rate, 200.0) # Cap the multiplier

def calculate_foundation_stability_index(soil_bearing: float, settlement: float, groundwater_level: float) -> float:
    base_index = max(soil_bearing - settlement * 10, 0.0)
    # Groundwater penalty (closer to surface = higher penalty)
    gw_penalty = 1.0
    if groundwater_level < 1.0:
        gw_penalty = 0.5
    elif groundwater_level < 3.0:
        gw_penalty = 0.8
        
    return base_index * gw_penalty

def calculate_load_stress_ratio(dead: float, live: float, wind: float, seismic: float, vibration: float, concrete_grade: str, steel_grade: str) -> float:
    total_load = dead + live + wind + seismic + vibration
    
    concrete_strength = float(''.join(filter(str.isdigit, concrete_grade)) or 30)
    steel_strength = float(''.join(filter(str.isdigit, steel_grade)) or 500)
    
    # Heuristic capacity
    expected_capacity = (concrete_strength * 2) + (steel_strength * 0.5)
    
    ratio = total_load / expected_capacity if expected_capacity > 0 else 1.0
    return ratio

def run_structural_calculations(data: EngineeringInput) -> dict:
    age = data.building_info.construction_year
    current_year = datetime.now().year
    age_years = max(current_year - age, 0)
    
    concrete_durability = calculate_concrete_durability_factor(
        data.structural_model.concrete_grade,
        age_years,
        data.structural_model.crack_width,
        data.structural_model.water_cement_ratio
    )
    
    corrosion_rate = calculate_corrosion_rate_multiplier(
        data.structural_model.corrosion_level,
        data.environmental_model.coastal_exposure,
        data.environmental_model.humidity,
        data.environmental_model.moisture_sensor_baseline
    )
    
    foundation_index = calculate_foundation_stability_index(
        data.structural_model.soil_bearing_capacity,
        data.structural_model.settlement_value,
        data.structural_model.groundwater_level
    )
    
    load_stress = calculate_load_stress_ratio(
        data.load_model.dead_load,
        data.load_model.live_load,
        data.load_model.wind_load,
        data.load_model.seismic_load,
        data.load_model.vibration_load,
        data.structural_model.concrete_grade,
        data.structural_model.steel_grade
    )
    
    return {
        "concrete_durability_factor": round(concrete_durability, 2),
        "corrosion_rate_multiplier": round(corrosion_rate, 2),
        "foundation_stability_index": round(foundation_index, 2),
        "load_stress_ratio": round(load_stress, 4)
    }
