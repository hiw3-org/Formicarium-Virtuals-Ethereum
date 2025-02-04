from fastapi import FastAPI
from routes import router as api_router

# Initialize the FastAPI app
app = FastAPI(
    title="Agent AI API",
    description="API for interacting with the Formicarium keychain AI chatbot.",
    version="1.0.0",
)

# Include the API routes
app.include_router(api_router, prefix="/api")

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

    uvicorn.run(app, host="localhost", port=8000)
