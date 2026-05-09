from app.schemas.building import EngineeringInput
from app.calculations.structural import run_structural_calculations
from app.chains.analysis import run_analysis_chain
from datetime import datetime

MAX_LIFESPANS = {
    "residential": 80,
    "commercial": 60,
    "industrial": 50,
    "bridge": 100,
    "hospital": 70
}

def process_prediction(data: EngineeringInput) -> dict:
    # 1. Run Structural Calculations
    calc_results = run_structural_calculations(data)
    
    # 2. Run AI Analysis
    ai_results = run_analysis_chain(data, calc_results)
    
    # 3. Output Synthesis & Final Calculation
    current_year = datetime.now().year
    age = max(current_year - data.building_info.construction_year, 0)
    
    base_health = ai_results.get("ai_base_score", 80)
    degradation_velocity = ai_results.get("degradation_velocity", 5)
    
    load_stress = calc_results["load_stress_ratio"]
    corrosion_rate = calc_results["corrosion_rate_multiplier"]
    
    load_penalty = max(0, (load_stress - 1.0) * 50) 
    corrosion_penalty = min(corrosion_rate * 0.5, 30)
    
    structural_health_score = max(base_health - load_penalty - corrosion_penalty, 0.0)
    
    btype = data.building_info.building_type.lower()
    max_life = 60 
    for key, val in MAX_LIFESPANS.items():
        if key in btype:
            max_life = val
            break
            
    penalty_years = degradation_velocity * (age / 10.0) if age > 0 else 0
    rul = max(max_life - age - penalty_years, 0)
    estimated_lifespan = age + rul
    
    base_failure_prob = 100 - structural_health_score
    ai_failure_prob = ai_results.get("failure_probability", base_failure_prob)
    final_failure_prob = max(base_failure_prob, ai_failure_prob)

    # Immediate risk uplift when clear anomaly-like input conditions exist.
    anomaly_boost = 0.0
    if data.load_model.vibration_load >= 8.0:
        anomaly_boost += 20.0
    if data.structural_model.crack_width >= 1.0:
        anomaly_boost += 15.0
    final_failure_prob += anomaly_boost
    final_failure_prob = min(final_failure_prob, 100.0)

    if structural_health_score >= 80:
        structural_risk_level = "Safe"
    elif structural_health_score >= 60:
        structural_risk_level = "Moderate"
    elif structural_health_score >= 40:
        structural_risk_level = "Risky"
    else:
        structural_risk_level = "Critical"
    
    # Graph Data Generation
    years = [current_year, current_year + 5, current_year + 10, current_year + 15, current_year + 20]
    health_score_trend = []
    current_score = structural_health_score
    for _ in years:
        health_score_trend.append(max(round(current_score, 2), 0))
        current_score -= (degradation_velocity * 0.5 * 5) # Decrease over 5 years

    prediction_data = {
        "estimated_lifespan_years": round(estimated_lifespan, 1),
        "structural_health_score": round(structural_health_score, 2),
        "failure_probability_pct": round(final_failure_prob, 2),
        "corrosion_severity": round(calc_results["corrosion_rate_multiplier"], 2),
        "crack_growth_trend": "Increasing" if data.structural_model.crack_width > 0.5 else "Stable",
        "maintenance_priority": ai_results.get("maintenance_priority", "Medium"),
        "structural_risk_level": ai_results.get("risk_level", structural_risk_level),
        "lifespan_graph": {
            "years": years,
            "health_score": health_score_trend
        },
        "recommendations": ai_results.get("recommendations", [])
    }
    
    return prediction_data
