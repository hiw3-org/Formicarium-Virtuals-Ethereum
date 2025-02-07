from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as api_router

# Initialize the FastAPI app
app = FastAPI(
    title="Agent AI API",
    description="API for interacting with the Formicarium keychain AI chatbot.",
    version="1.0.0",
)

# Add this after initializing your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict access to specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the API routes
app.include_router(api_router, prefix="/agent")

# Print the API routes in console
for route in app.routes:
    print(route)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Agent AI API!"}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
