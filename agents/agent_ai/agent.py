import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv
import time

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agents.agent_ai.keychain_design_tools import generate_keychain_stl_tool, generate_image_tool, generate_keychain_gcode_tool
from agents.agent_ai.prompts import agent_prompt_v0
from agents.agent_ai.config import model, wallet_data_file

load_dotenv()

# Dictionary to store agent instances for each user
user_agents: Dict[str, Any] = {}
# Dictionary to track the last activity time for each user
user_last_activity: Dict[str, float] = {}


def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM.
    llm = ChatOpenAI(model=model)

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

    # persist the agent's CDP MPC Wallet Data.
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)

    # Initialize CDP Agentkit Toolkit and get tools.
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools() + [generate_keychain_stl_tool, generate_image_tool, generate_keychain_gcode_tool]

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config_llm = {"configurable": {"thread_id": "3D keychain printer"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=agent_prompt_v0,
    ), config_llm
    
def get_or_create_agent(api_key: str):
    """Get or create an agent instance for the user."""
    if api_key not in user_agents:
        # Initialize a new agent for the user
        llm = ChatOpenAI(model=model, api_key=api_key)
        memory = MemorySaver()
        config = {"configurable": {"thread_id": api_key}}  # Use API key as the thread ID
        
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
        tools = cdp_toolkit.get_tools() + [generate_keychain_stl_tool, generate_image_tool, generate_keychain_gcode_tool]

        agent_executor = create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=agent_prompt_v0,  # Replace with your prompt modifier
        )

        # Store the agent instance and its config
        user_agents[api_key] = {
            "agent_executor": agent_executor,
            "config": config,  # Save the config for later use
        }

    user_last_activity[api_key] = time.time()
    return user_agents[api_key]


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


def run_chat_mode(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Run agent with the user's input in chat mode
            for chunk in agent_executor.stream({"messages": [HumanMessage(content=user_input)]}, config):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
            print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


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


def run_agent():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()
    run_chat_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    run_agent()
