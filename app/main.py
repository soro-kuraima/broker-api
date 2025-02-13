import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .controllers import auth, csv_operations
from .database import Base, engine
from .services.number_generator import number_generator
from .controllers.websocket import router as websocket_router

# Create database tables
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(csv_operations.router, prefix=settings.API_V1_STR)

# Include the WebSocket router
app.include_router(websocket_router, prefix=settings.API_V1_STR)

    

@app.on_event("startup")
async def startup_event():
    number_generator.start()
    print("Available routes:", [route.path for route in app.routes])

@app.on_event("shutdown")
async def shutdown_event():
    number_generator.stop()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)