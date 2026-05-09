import os
import json
from dotenv import load_dotenv

load_dotenv()
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from app.prompts.engineering import STRUCTURAL_ENGINEER_PROMPT, ENVIRONMENTAL_CONTEXT_PROMPT, RISK_ANALYST_PROMPT
from app.schemas.building import EngineeringInput

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    model_name = os.getenv("GROQ_MODEL", "qwen-2.5-72b-instruct")
    return ChatGroq(model_name=model_name, api_key=api_key, temperature=0.2)

def get_default_recommendations(base_score: int, degradation_velocity: int, load_stress: float, risk_level: str) -> list:
    """Generate context-aware fallback recommendations based on structural parameters."""
    recommendations = []
    
    # Health-based recommendations
    if base_score < 40:
        recommendations.append("CRITICAL: Immediate structural assessment required by licensed engineer.")
        recommendations.append("Emergency monitoring systems should be installed immediately.")
    elif base_score < 60:
        recommendations.append("Priority structural evaluation needed within 30 days.")
        recommendations.append("Establish enhanced monitoring protocols for critical areas.")
    elif base_score < 80:
        recommendations.append("Schedule routine structural inspection within 90 days.")
        recommendations.append("Review maintenance history and plan preventive interventions.")
    else:
        recommendations.append("Continue regular maintenance and periodic inspections.")
    
    # Degradation-based recommendations
    if degradation_velocity > 10:
        recommendations.append("High degradation rate detected: Accelerate maintenance schedule and increase inspection frequency.")
        recommendations.append("Consider accelerated remediation program for deteriorated components.")
    elif degradation_velocity > 5:
        recommendations.append("Moderate degradation observed: Implement preventive maintenance plan.")
    
    # Load stress recommendations
    if load_stress > 1.2:
        recommendations.append("Load stress ratio exceeds safe limits: Conduct load redistribution analysis.")
        recommendations.append("Evaluate capacity upgrades or load reduction strategies.")
    elif load_stress > 1.0:
        recommendations.append("Monitor load distribution closely; consider structural reinforcement.")
    
    # Risk level recommendations
    if risk_level == "Critical":
        recommendations.append("URGENT: Restrict building access and limit occupancy until cleared by structural engineer.")
    elif risk_level == "Risky":
        recommendations.append("Document current condition with photography and detailed assessment.")
        recommendations.append("Prepare emergency response plan and evacuation procedures.")
    
    # Ensure we have at least 3 recommendations
    if len(recommendations) < 3:
        recommendations.extend([
            "Schedule regular professional inspections at least annually.",
            "Maintain detailed records of all maintenance and repairs.",
            "Address any environmental factors (moisture, corrosion, chemical exposure) proactively."
        ])
    
    return recommendations[:5]  # Return top 5 recommendations

def run_analysis_chain(data: EngineeringInput, calc_results: dict) -> dict:
    llm = get_llm()
    
    # 1. Structural Context AI
    structural_chain = STRUCTURAL_ENGINEER_PROMPT | llm | StrOutputParser()
    try:
        base_score_str = structural_chain.invoke({
            "building_type": data.building_info.building_type,
            "durability": calc_results["concrete_durability_factor"],
            "corrosion": calc_results["corrosion_rate_multiplier"],
            "foundation": calc_results["foundation_stability_index"],
            "load_stress": calc_results["load_stress_ratio"],
            "material_inputs": f"Concrete: {data.structural_model.concrete_grade}, Steel: {data.structural_model.steel_grade}"
        })
        base_score = int(''.join(filter(str.isdigit, base_score_str)) or 80)
    except Exception as e:
        print("Structural chain error:", repr(e))
        base_score = 80
        
    # 2. Environmental Context AI
    env_factors = f"Temp: {data.environmental_model.temperature}C, Humidity: {data.environmental_model.humidity}%, Coastal: {data.environmental_model.coastal_exposure}, Pollution: {data.environmental_model.pollution_level}, Rainfall: {data.environmental_model.rainfall}mm"
    
    env_chain = ENVIRONMENTAL_CONTEXT_PROMPT | llm | StrOutputParser()
    try:
        deg_vel_str = env_chain.invoke({
            "base_score": base_score,
            "env_factors": env_factors
        })
        degradation_velocity = int(''.join(filter(str.isdigit, deg_vel_str)) or 5)
    except Exception as e:
        print("Environmental chain error:", repr(e))
        degradation_velocity = 5

    # Router Logic: modify prompt context based on building_type
    btype = data.building_info.building_type.lower()
    if "hospital" in btype:
        btype_context = f"{data.building_info.building_type} (Strict seismic & operational load priority)"
    elif "bridge" in btype:
        btype_context = f"{data.building_info.building_type} (Dynamic vibration & wind load priority)"
    else:
        btype_context = data.building_info.building_type

    sensor_anomalies = f"Moisture Baseline: {data.environmental_model.moisture_sensor_baseline}%. No active tilt/vibration alerts."

    # 3. Risk AI - with improved error handling
    risk_chain = RISK_ANALYST_PROMPT | llm
    try:
        risk_assessment_str = risk_chain.invoke({
            "building_type": btype_context,
            "base_score": base_score,
            "degradation_velocity": degradation_velocity,
            "load_stress": calc_results["load_stress_ratio"],
            "sensor_anomalies": sensor_anomalies
        })
    except Exception as invoke_exc:
        print("Risk chain invoke error:", repr(invoke_exc))
        risk_assessment_str = ""

    print("Raw risk AI output:", risk_assessment_str[:500] if risk_assessment_str else "(empty)")
    
    # Parse JSON with enhanced error handling
    try:
        json_str = risk_assessment_str
        if not json_str or not json_str.strip():
            raise ValueError("Empty response from LLM")
            
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        parser = JsonOutputParser()
        risk_result = parser.parse(json_str.strip())
        print("✓ Risk JSON parsed successfully")
    except Exception as parse_exc:
        print("Risk JSON parse error:", repr(parse_exc))
        
        # Generate context-aware fallback recommendations
        fallback_risk_level = "Unknown"
        if base_score < 40:
            fallback_risk_level = "Critical"
        elif base_score < 60:
            fallback_risk_level = "Risky"
        elif base_score < 80:
            fallback_risk_level = "Moderate"
        else:
            fallback_risk_level = "Safe"
        
        fallback_recommendations = get_default_recommendations(
            base_score, degradation_velocity, 
            calc_results["load_stress_ratio"], 
            fallback_risk_level
        )
        
        risk_result = {
            "failure_probability": 50.0 if fallback_risk_level == "Unknown" else (85.0 if fallback_risk_level == "Critical" else (60.0 if fallback_risk_level == "Risky" else 30.0)),
            "risk_level": fallback_risk_level,
            "maintenance_priority": "High",
            "recommendations": fallback_recommendations
        }
        print(f"✓ Using fallback recommendations: {len(fallback_recommendations)} items")
        
    risk_result["ai_base_score"] = base_score
    risk_result["degradation_velocity"] = degradation_velocity
    
    return risk_result
