from langchain_core.prompts import PromptTemplate

STRUCTURAL_ENGINEER_PROMPT = PromptTemplate(
    input_variables=["building_type", "durability", "corrosion", "foundation", "load_stress", "material_inputs"],
    template="""You are an expert Structural Engineer AI.
Analyze the structural data for a {building_type}:
- Concrete Durability Factor: {durability}
- Corrosion Rate Multiplier: {corrosion}
- Foundation Stability Index: {foundation}
- Load Stress Ratio: {load_stress}
- Materials: {material_inputs}

Based on these deterministic engineering values, determine an initial Base Health Score between 0 and 100.
Return ONLY the integer value (0-100)."""
)

ENVIRONMENTAL_CONTEXT_PROMPT = PromptTemplate(
    input_variables=["base_score", "env_factors"],
    template="""You are an Environmental Context AI.
The building currently has a Base Health Score of {base_score} out of 100.
Consider the following climate severity factors:
{env_factors}

Determine the Degradation Velocity (Penalty Years per decade).
Return ONLY the integer value representing the Degradation Velocity penalty (0-20)."""
)

RISK_ANALYST_PROMPT = PromptTemplate(
    input_variables=["building_type", "base_score", "degradation_velocity", "load_stress", "sensor_anomalies"],
    template="""You are an expert Risk Analyst AI for structural engineering.
Building Type: {building_type}
Base Health Score: {base_score}
Degradation Velocity (Penalty): {degradation_velocity}
Load Stress Ratio: {load_stress}
Sensor Anomalies: {sensor_anomalies}

Analyze the risk comprehensively and return ONLY a valid JSON object with NO markdown, NO code blocks, NO extra text. JSON structure MUST be:
{{
    "failure_probability": <float 0-100>,
    "risk_level": "<one of: Safe, Moderate, Risky, Critical>",
    "maintenance_priority": "<one of: Low, Medium, High, Immediate>",
    "recommendations": [
        "<specific actionable recommendation 1>",
        "<specific actionable recommendation 2>",
        "<specific actionable recommendation 3>",
        "<specific actionable recommendation 4>",
        "<specific actionable recommendation 5>"
    ]
}}

Recommendations MUST be:
- Specific to the building type and condition
- Actionable and prioritized
- Based on the health score, degradation velocity, and load stress
- Written in professional engineering language
- At least 3-5 detailed recommendations

Output ONLY valid JSON. Start with {{ and end with }}."""
)
