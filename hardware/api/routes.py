import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from hardware.api.agent_controller import ChatRequest, ChatResponse, process_chat_request
from hardware.api.gcode_controller import STLRequest, handle_stl_request

router = APIRouter()

logging.basicConfig(level=logging.INFO)

# OctoPrint Camera Stream URL
octoprint_camera_url = "http://192.168.0.220/webcam/?action=stream"
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


@router.post("/create_order_request", response_model=ChatResponse)
async def chat(request: ChatRequest):

    """
    Endpoint for handling chat requests.
    """
    # Tle not pride file (gcoda)
    # On sam pol kliče openai api, da dobi price_per_kg in prie elektrike
    # In pol sam kliče tool za calculate 
    try:
        response = process_chat_request(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# The API route to handle the G-code generation request
@router.post("/get_gcode")
async def get_gcode(request: STLRequest):
    try:
        # Call the controller to handle the STL request and generate G-code
        gcode_path = handle_stl_request(request.stl_file, request.stl_name, request.box_size)
        
        # Return the G-code path in the response
        return {"gcode_path": gcode_path}
    
    except Exception as e:
        # Raise HTTP exception with error details if something goes wrong
        raise HTTPException(status_code=500, detail=str(e))


