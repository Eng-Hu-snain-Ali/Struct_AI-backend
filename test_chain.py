import asyncio
from app.schemas.building import EngineeringInput, BuildingInfo, StructuralModel, EnvironmentalModel, LoadModel
from app.chains.analysis import run_analysis_chain

async def test():
    data = EngineeringInput(
        building_info=BuildingInfo(building_name="A", building_type="Commercial", construction_year=2000, floors=10, total_area=5000, location="City"),
        structural_model=StructuralModel(concrete_grade="30", steel_grade="Fe500", crack_width=0.2, corrosion_level=15, reinforcement_diameter=16),
        environmental_model=EnvironmentalModel(temperature=28, humidity=65, rainfall=120, pollution_level="High", coastal_exposure=False),
        load_model=LoadModel(dead_load=120, live_load=50, wind_load=30, seismic_load=20, vibration_load=5)
    )
    calc_results = {
        "concrete_health_indicator": 80,
        "corrosion_severity_indicator": 20,
        "load_capacity_risk_indicator": 10
    }
    try:
        res = await run_analysis_chain(data, calc_results)
        print("Success:", res)
    except Exception as e:
        print("Error:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
