from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from agent_controller import ChatRequest, ChatResponse, process_chat_request
from media_controller import get_image_by_name, ImageRequest, ImageResponse

# Define the router
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):

    """
    Endpoint for handling chat requests.
    """
    try:
        response = process_chat_request(request, background_tasks)
        return response
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-image", response_model=ImageResponse)
async def get_image(request: ImageRequest):
    """
    Endpoint to retrieve an image from local storage based on the provided image name.
    """
    return get_image_by_name(request.image_name)
