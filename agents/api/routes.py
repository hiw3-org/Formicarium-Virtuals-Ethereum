from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agents.agent_ai.agent import chat_with_agent, initialize_agent

# Initialize the agent
agent_executor, config = initialize_agent()


# Define the router
router = APIRouter()


# Request model for the chat endpoint
class ChatRequest(BaseModel):
    prompt: str


# Response model for the chat endpoint
class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat requests from the frontend.
    """
    try:
        # Call the agent with the user's prompt
        result = chat_with_agent(request.prompt, agent_executor, config)
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
