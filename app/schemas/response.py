from pydantic import BaseModel
from typing import Any, Optional, Dict, List

class StandardResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = {}
    timestamp: str

class LifespanGraph(BaseModel):
    years: List[int]
    health_score: List[float]

class PredictionData(BaseModel):
    estimated_lifespan_years: float
    structural_health_score: float
    failure_probability_pct: float
    corrosion_severity: float
    crack_growth_trend: str
    maintenance_priority: str
    structural_risk_level: str
    lifespan_graph: LifespanGraph
    recommendations: List[str]
