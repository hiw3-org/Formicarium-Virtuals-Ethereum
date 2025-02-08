import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv
import time

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hardware.agent_ai.calculator_tools import estimate_print_time, calculate_3d_printing_cost
from hardware.agent_ai.octoprint_tools import upload_file_to_octoprint, start_printing
from hardware.agent_ai.prompts import user_agent_prompt
from hardware.agent_ai.config import model, wallet_data_file

load_dotenv()

# Dictionary to store agent instances for each user
user_agents: Dict[str, Any] = {}
# Dictionary to track the last activity time for each user
user_last_activity: Dict[str, float] = {}

def get_or_create_agent(user_id):
    """Get or create an agent instance for the user."""
    if user_id not in user_agents:
        # Initialize a new agent for the user
        llm = ChatOpenAI(model=model)
        memory = MemorySaver()
        config = {"configurable": {"thread_id": user_id}}  # Use API key as the thread ID
        
        wallet_data = None

        if os.path.exists(wallet_data_file):
            with open(wallet_data_file) as f:
                wallet_data = f.read()
        
        # Configure CDP Agentkit Langchain Extension.
        values = {}
        if wallet_data is not None:
            # If there is a persisted agentic wallet, load it and pass to the CDP Agentkit Wrapper.
            values = {"cdp_wallet_data": wallet_data}

        agentkit = CdpAgentkitWrapper(**values)
        
        # Initialize CDP Agentkit Toolkit and get tools.
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools() + [estimate_print_time, 
                                           calculate_3d_printing_cost,
                                           upload_file_to_octoprint,
                                           start_printing
                                           ]

        agent_executor = create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=user_agent_prompt,  # Replace with your prompt modifier
        )

        # Store the agent instance and its config
        user_agents[user_id] = {
            "agent_executor": agent_executor,
            "config": config,  # Save the config for later use 
        }

    user_last_activity[user_id] = time.time()
    return user_agents[user_id]


def cleanup_inactive_agents(max_inactive_time: float = 3600):
    """
    Remove agent instances for users who have been inactive for too long.

    Args:
        max_inactive_time (float): Maximum allowed inactivity time in seconds.
                                  Default is 1 hour (3600 seconds).
    """
    current_time = time.time()
    inactive_users = [
        api_key for api_key, last_activity in user_last_activity.items()
        if current_time - last_activity > max_inactive_time
    ]

    for api_key in inactive_users:
        # Remove the agent instance and its activity record
        del user_agents[api_key]
        del user_last_activity[api_key]


def chat_with_agent(user_input, agent_executor, config):
    """Run the agent interactively based on user request."""
    try:
        # Initialize the message history with the user's input
        messages = [HumanMessage(content=user_input)]

        # Stream the agent's response
        for chunk in agent_executor.stream({"messages": messages}, config):
            if "agent" in chunk:
                # Handle agent messages
                agent_message = chunk["agent"]["messages"][0]
                messages.append(agent_message)

            elif "tools" in chunk:
                tool_message = chunk["tools"]["messages"][0]
                messages.append(tool_message)

        # Return the final response from the agent
        return messages[-1].content

    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")
