from fastapi import FastAPI
from routes.analysis_routes import analysis_router
from routes.brand_routes import brand_router
from services.helpers import get_env_value
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Include the analysis router
app.include_router(analysis_router, prefix="/analyze", tags=["Content Analysis"])
app.include_router(brand_router, prefix="/brand", tags=["Brand"])


# Main entry point for the app, running via Uvicorn if __name__ == "__main__"
if __name__ == "__main__":
    port: str = get_env_value("PORT", default="8000")  # Default port is 8000 if not set in the environment
    uvicorn.run("main:app", host="0.0.0.0", port=int(port), log_level="info", reload=True)
