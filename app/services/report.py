import json
import os
import aiofiles
from datetime import datetime

async def generate_json_report(building_id: int, prediction_data: dict) -> str:
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{report_dir}/report_building_{building_id}_{timestamp}.json"
    
    async with aiofiles.open(filename, mode='w') as f:
        await f.write(json.dumps(prediction_data, indent=4))
        
    return filename
