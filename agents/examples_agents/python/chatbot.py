import os
import sys
import time
import requests
from pathlib import Path

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

import openai

# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet_data.txt"

load_dotenv()


def generate_image(prompt: str) -> str:
    """Generate an image using DALL·E and return the image URL."""
    response = openai.images.generate(
        model="dall-e-3",  # Use "dall-e-2" if you prefer
        prompt=prompt,
        n=1,  # Number of images to generate
        size="1024x1024",  # Image size
        response_format="url",  # Return image URL
    )
    # Access the URL using attribute access
    return response.data[0].url


@tool
def generate_image_tool(prompt: str) -> str:
    """Generate a grayscale image based on the user's prompt and save it locally."""
    # Ensure the image is grayscale
    grayscale_prompt = f"{prompt} in grayscale"
    image_url = generate_image(grayscale_prompt)

    # Download the image
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download image: {response.status_code}")

    # Save the image to a folder
    output_folder = Path("generated_images")
    output_folder.mkdir(exist_ok=True)  # Create the folder if it doesn't exist

    # Sanitize the prompt to create a valid filename
    sanitized_prompt = "".join(c for c in prompt if c.isalnum() or c in (" ", "_")).rstrip()
    image_path = output_folder / f"{sanitized_prompt.replace(' ', '_')}.png"

    with open(image_path, "wb") as f:
        f.write(response.content)

    return f"Image saved to: {image_path}"


def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM.
    llm = ChatOpenAI(model="gpt-4o-mini")

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
    tools = cdp_toolkit.get_tools() + [generate_image_tool]

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a helpful agent (that can interact onchain using the Coinbase Developer Platform AgentKit). "
            "Your primary focus is to assist users (with the creation of keychain 3D prints). "
            "Your first goal is to create a 2D image (that the user requested). "
            "The image must be grayscale, never colored. "
            "To generate the image, use the `generate_image_tool` tool with a detailed description of the image. "
            "After the user confirms (that the image is correct), you will call the Python script (called img2stl.py) and input the image. "
            "That script should output an STL file (that you will return to the user). "
            "When the user confirms (that he is happy with the provided keychain), you will calculate (how much that print will cost him). "
            "When the user sends you the funds (to your wallet), you will initiate the 3D print. "
            "You are empowered (to interact onchain using your tools). If you ever need funds, you can request them "
            "(from the faucet if you are on network ID base-sepolia). If not, you can provide your wallet details (and request funds from the user). "
            "Before executing your first action, get the wallet details (to see what network you're on). If there is a 5XX (internal HTTP error code), ask the user (to try again later). "
            "If someone asks you to do something (that is not connected with 3D printing of keychains), kindly remind them (that you can only help them with the creation of 3D-printed keychains and nothing else). "
            "Refrain from restating your tools' descriptions (unless it is explicitly requested)."
        ),
    ), config


# Chat Mode
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
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()

    run_chat_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
