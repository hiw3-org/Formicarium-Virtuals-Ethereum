from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException, Request, BackgroundTasks
import os
import re
import base64
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.agent_ai.agent import chat_with_agent, initialize_agent, get_or_create_agent, cleanup_inactive_agents

# Initialize the agent
agent_executor, config = initialize_agent()

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
    
    
def fetch_api_key_from_header(req: Request) -> str:
    """
    Fetch the API key from the request headers.
    """
    if "api-key" in req.headers:
        return req.headers["api-key"]
    else:
        raise HTTPException(status_code=401, detail="No API key provided")



def process_chat_request(request: ChatRequest, req: Request, background_tasks: BackgroundTasks) -> ChatResponse:
    """
    Handle the chat request and return a structured response.
    """
    try:        
        # Fetch the API key from the headers
        api_key = fetch_api_key_from_header(req)
    
        # Get or create the agent for the user
        agent_data = get_or_create_agent(api_key)
        agent_executor = agent_data["agent_executor"]
        config = agent_data["config"]  # Retrieve the config
        
        
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
                        
        background_tasks.add_task(cleanup_inactive_agents)

        # Remove file references from the response text
        cleaned_response = file_pattern.sub('', result).strip()
        cleaned_response = cleaned_response.replace("\n\n", "\n").strip()

        return ChatResponse(response=cleaned_response, stl_file=stl_file, image_file=image_file)

    except Exception as e:
        raise ValueError(f"Error processing request: {str(e)}")
