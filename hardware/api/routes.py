from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx

# Define the router
router = APIRouter()

# OctoPrint Camera Stream URL
octoprint_camera_url = "http://192.168.221.144/webcam/?action=stream"

async def generate_camera_stream():
    """Generator function to stream OctoPrint camera feed using httpx."""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Api-Key": "fBV0WeIfD_oOQs18gKwnOMGY2-nmsU5y_n44EVh8iwY"}
            async with client.stream("GET", octoprint_camera_url, headers=headers, timeout=10) as r:
                if r.status_code != 200:
                    raise HTTPException(status_code=r.status_code, detail="Failed to fetch camera stream")

                async for chunk in r.aiter_bytes(chunk_size=8192):  # Async streaming
                    yield chunk  # Stream chunks in real-time
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to OctoPrint: {str(e)}")

@router.get("/camera_stream")
async def stream_camera():
    """FastAPI endpoint to proxy the camera stream."""
    return StreamingResponse(generate_camera_stream(), media_type="multipart/x-mixed-replace; boundary=frame")
