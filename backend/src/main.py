from fastapi import FastAPI
from src.api.routes import router as api_router
from src.storage.elastic_client import es_service
import uvicorn

# Application Description 
app = FastAPI(title="LightSIEM Core", version="0.4.0 (Modular Architecture)")

# Port
app.include_router(api_router, prefix="/api")

@app.get("/")
def health_check():
    """Checks whether the system is up and running."""
    db_status = "Connected" if es_service.is_connected() else "Disconnected"
    return {
        "status": "active", 
        "version": "Phase-4-Modular", 
        "storage": db_status
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)






