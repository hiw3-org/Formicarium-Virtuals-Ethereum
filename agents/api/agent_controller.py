from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException, Request, BackgroundTasks
import os
import re
import base64
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.agent_ai.agent import chat_with_agent, get_or_create_agent, cleanup_inactive_agents
from agents.agent_ai.keychain_design_tools import convert_stl_to_image

# Request model for the chat endpoint
class ChatRequest(BaseModel):
    user_id: int
    prompt: str

# Response model for the chat endpoint
class FileData(BaseModel):
    filename: str
    content: str  # Base64-encoded content
    content_type: str
    
class ChatHistoryItem(BaseModel):
    role: str  # 'user' or 'agent'
    message: str

# Response model for the chat endpoint
class ChatResponse(BaseModel):
    response: str
    stl_file: Optional[FileData] = None
    image_file: Optional[FileData] = None
    chat_history: list[ChatHistoryItem] = None
    

def process_chat_request(request: ChatRequest, background_tasks: BackgroundTasks) -> ChatResponse:
    """
    Handle the chat request and return a structured response.
    """
    try:        
    
        # Get or create the agent for the user
        agent_data = get_or_create_agent(request.user_id)
        agent_executor = agent_data["agent_executor"]
        config = agent_data["config"]  # Retrieve the config
        history = agent_data["history"]  # Retrieve the conversation history
        
        # Append the user's prompt to history
        history.append({"role": "user", "message": request.prompt})
        
        # Call the agent with the user's prompt
        result = chat_with_agent(request.prompt, agent_executor, config)
        
        history.append({"role": "agent", "message": result})

        # Extract file references from the response
        file_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
        file_paths = file_pattern.findall(result)

        stl_file = None
        image_file = None

        for file_path in file_paths:
            if os.path.exists(file_path):
                
                with open(file_path, "rb") as file:
                    
                    if file_path.endswith(".stl"):
                        # Convert the STL file to an image
                        output_path = convert_stl_to_image(file_path)
                        
                        with open(output_path, "rb") as file:
                        
                            file_data = file.read()
                            encoded_content = base64.b64encode(file_data).decode("utf-8")
                            file_name = os.path.basename(output_path)

                            stl_file = FileData(
                                filename=file_name,
                                content=encoded_content,
                                content_type="image/png"
                            )

                    elif file_path.endswith(".png"):
                        file_data = file.read()
                        encoded_content = base64.b64encode(file_data).decode("utf-8")
                        file_name = os.path.basename(file_path)

                        image_file = FileData(
                            filename=file_name,
                            content=encoded_content,
                            content_type="image/png"
                        )

                        
        background_tasks.add_task(cleanup_inactive_agents)

        # Remove file references from the response text
        cleaned_response = file_pattern.sub('', result).strip()
        cleaned_response = cleaned_response.replace("\n\n", "\n").strip()

        return ChatResponse(response=cleaned_response, 
                            stl_file=stl_file, 
                            image_file=image_file,
                            chat_history=history)

    except Exception as e:
        raise ValueError(f"Error processing request: {str(e)}")
