from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from agent_controller import ChatRequest, ChatResponse, process_chat_request

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
