from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.websocket.monitor import router as websocket_router
import asyncio

app = FastAPI(
    title="AI-Based Building Lifespan Prediction System API",
    description="Backend system for structural engineering analysis",
    version="1.0.0"
)

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://lablab-ai-amd-developer-hackathon-struct-ai-predictor.hf.space",
     # Direct HF App link
    "https://huggingface.co/spaces/lablab-ai-amd-developer-hackathon/Struct_AI_Predictor", # HF Repo link
    "https://struct-ai-frontend.vercel.app", # REPLACE THIS with your actual live Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix="/api", tags=["Core Endpoints"])
app.include_router(websocket_router, prefix="/api", tags=["WebSockets"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Based Building Lifespan Prediction System API"}
