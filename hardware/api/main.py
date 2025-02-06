from fastapi import FastAPI
from routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI(
    title="3D Printer API",
    description="API for interacting with the consumers of the service.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for debugging)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes with prefix "/api"
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the 3D printer API!"}

# Debugging route: Check available endpoints
@app.get("/routes")
async def get_routes():
    return [route.path for route in app.router.routes]

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
