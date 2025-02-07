import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter()

logging.basicConfig(level=logging.INFO)

# OctoPrint Camera Stream URL
octoprint_camera_url = "http://192.168.221.144/webcam/?action=stream"
# octoprint_camera_url = "http://97.68.104.34/mjpg/video.mjpg" TEST URL



async def generate_camera_stream():
    """Corrected generator function for MJPEG streaming."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            headers = {"X-Api-Key": "fBV0WeIfD_oOQs18gKwnOMGY2-nmsU5y_n44EVh8iwY"}
            async with client.stream("GET", octoprint_camera_url, headers=headers) as r:
                logging.info(f"Received status code: {r.status_code}")

                if r.status_code != 200:
                    raise HTTPException(status_code=r.status_code, detail="Failed to fetch camera stream")

                buffer = b""
                async for chunk in r.aiter_bytes(chunk_size=8192):
                    buffer += chunk
                    
                    while b'\xff\xd8' in buffer and b'\xff\xd9' in buffer:
                        start = buffer.index(b'\xff\xd8')  # JPEG Start
                        end = buffer.index(b'\xff\xd9') + 2  # JPEG End
                        frame = buffer[start:end]
                        buffer = buffer[end:]  # Remove processed frame
                        
                        yield (b"--frame\r\n"
                               b"Content-Type: image/jpeg\r\n\r\n" +
                               frame +
                               b"\r\n")

    except httpx.RequestError as e:
        logging.error(f"Error connecting to OctoPrint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to OctoPrint: {str(e)}")


@router.get("/camera_stream")
async def stream_camera():
    """FastAPI endpoint to proxy the camera stream."""
    return StreamingResponse(generate_camera_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

