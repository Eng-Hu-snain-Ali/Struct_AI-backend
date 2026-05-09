from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime

from app.schemas.building import EngineeringInput, SensorInput
from app.schemas.response import StandardResponse
from app.services.prediction import process_prediction
from app.services.sensor import process_sensor_data
from app.services.report import generate_json_report

router = APIRouter()

@router.post("/predict-lifespan", response_model=StandardResponse)
def predict_lifespan(data: EngineeringInput):
    try:
        prediction_data = process_prediction(data)
        return StandardResponse(
            status="success",
            message="Analysis completed",
            data=prediction_data,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-risk", response_model=StandardResponse)
def analyze_risk(data: EngineeringInput):
    # Reusing predict_lifespan logic as it covers risk as well for now
    try:
        prediction_data = process_prediction(data)
        return StandardResponse(
            status="success",
            message="Risk Analysis completed",
            data={
                "failure_probability_pct": prediction_data["failure_probability_pct"],
                "structural_risk_level": prediction_data["structural_risk_level"],
                "maintenance_priority": prediction_data["maintenance_priority"]
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-sensor-data", response_model=StandardResponse)
def upload_sensor_data(data: SensorInput):
    try:
        result = process_sensor_data(data)
        return StandardResponse(
            status="success",
            message="Sensor data processed",
            data=result,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate-report", response_model=StandardResponse)
async def generate_report(building_id: int):
    try:
        # For demonstration, we would query the latest prediction
        # but here we'll just mock generating it using existing data
        mock_data = {"building_id": building_id, "status": "simulated report generated"}
        file_path = await generate_json_report(building_id, mock_data)
        
        return StandardResponse(
            status="success",
            message="Report generated successfully",
            data={"report_url": file_path},
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=StandardResponse)
def get_history(building_id: int):
    # This would normally query the DB
    return StandardResponse(
        status="success",
        message="History retrieved (DB disabled)",
        data={"history": []},
        timestamp=datetime.now().isoformat()
    )
