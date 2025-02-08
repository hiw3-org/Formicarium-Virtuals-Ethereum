from fastapi import FastAPI
from routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
from hardware.agent_ai.blockchain_tools import listen_events
from hardware.agent_ai.octoprint_tools import poll_octoprint_status  # Import the polling function

# Initialize global variable for previous state
previous_state = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start both background tasks concurrently
    task1 = asyncio.create_task(listen_events())  # Blockchain events listener
    task2 = asyncio.create_task(poll_octoprint_status())  # OctoPrint status polling
    print("Background tasks started")

    yield  # This represents the lifespan of the FastAPI application

    # Once the application stops, cancel both background tasks
    task1.cancel()
    task2.cancel()
    try:
        await task1
        await task2
    except asyncio.CancelledError:
        pass

# Initialize the FastAPI app
app = FastAPI(
    title="3D Printer API",
    description="API for interacting with the consumers of the service.",
    version="1.0.0",
    lifespan=lifespan,  # Use the lifespan context manager
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
    uvicorn.run(app, host="0.0.0.0", port=8080)
