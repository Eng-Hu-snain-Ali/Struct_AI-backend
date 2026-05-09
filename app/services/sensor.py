from app.schemas.building import SensorInput

def process_sensor_data(data: SensorInput) -> dict:
    # 1. Basic Threshold checking to generate alerts
    alerts = []
    if data.crack_sensor > 2.0:
        alerts.append({"type": "Crack Expansion", "message": "Crack width exceeded safe threshold.", "severity": "Critical"})
    if data.vibration_sensor > 5.0:
        alerts.append({"type": "High Vibration", "message": "Abnormal structural vibration detected.", "severity": "High"})
        
    return {
        "stored": False,
        "alerts_generated": len(alerts),
        "alerts": alerts
    }
