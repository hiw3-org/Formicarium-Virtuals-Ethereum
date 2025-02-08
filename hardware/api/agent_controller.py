from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException, Request, BackgroundTasks
import os
import re
import base64
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hardware.agent_ai.agent import chat_with_agent, get_or_create_agent

# Request model for the chat endpoint
class ChatRequest(BaseModel):
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
    chat_history: list[ChatHistoryItem] = None
    

def process_chat_request(request: ChatRequest) -> ChatResponse:
    """
    Handle the chat request and return a structured response.
    """
    try:        
    
        # Get or create the agent for the user
        agent_data = get_or_create_agent("default")
        agent_executor = agent_data["agent_executor"]
        config = agent_data["config"]  # Retrieve the config        
        
        # Call the agent with the user's prompt
        result = chat_with_agent(request.prompt, agent_executor, config)

        # Extract file references from the response
        file_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

        # Remove file references from the response text
        cleaned_response = file_pattern.sub('', result).strip()
        cleaned_response = cleaned_response.replace("\n\n", "\n").strip()

        return ChatResponse(response=cleaned_response)

    except Exception as e:
        raise ValueError(f"Error processing request: {str(e)}")
