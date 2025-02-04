import os
import sys

from dotenv import load_dotenv

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
    config_llm = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=agent_prompt_v0,
    ), config_llm


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
