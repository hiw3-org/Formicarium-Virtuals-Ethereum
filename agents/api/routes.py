from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os
import re
import base64

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
class FileData(BaseModel):
    filename: str
    content: str  # Base64-encoded content
    content_type: str
    
# Response model for the chat endpoint
class ChatResponse(BaseModel):
    response: str
    stl_file: Optional[FileData] = None
    image_file: Optional[FileData] = None
    
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat requests from the frontend.
    """
    try:
        # Call the agent with the user's prompt
        result = chat_with_agent(request.prompt, agent_executor, config)

        # Extract file references from the response
        file_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
        file_paths = file_pattern.findall(result)

        stl_file = None
        image_file = None

        for file_path in file_paths:
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    file_data = file.read()
                    encoded_content = base64.b64encode(file_data).decode("utf-8")
                    file_name = os.path.basename(file_path)

                    if file_name.endswith(".stl"):
                        stl_file = FileData(
                            filename=file_name,
                            content=encoded_content,
                            content_type="application/octet-stream"
                        )
                    elif file_name.endswith(".png"):
                        image_file = FileData(
                            filename=file_name,
                            content=encoded_content,
                            content_type="image/png"
                        )

        # Remove file references from the response text
        cleaned_response = file_pattern.sub('', result).strip()
        cleaned_response = cleaned_response.replace("\n\n", "\n").strip()

        return ChatResponse(response=cleaned_response, stl_file=stl_file, image_file=image_file)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
