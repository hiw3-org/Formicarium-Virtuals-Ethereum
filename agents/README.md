# Formicarium - Agents AI

This directory contains the core (user) agent code and it's associated tools used within the Formicarium framework. The agent is responsible for various tasks such as generating images,generatig STL models, 3D model slicing (STL to G-code), and more. The agent can be accessed via the API layer for seamless communication and task execution.

## Overview
The agent is built with the [AgentKit](https://docs.cdp.coinbase.com/agentkit/docs/welcome) framework. THe biggest plus being that the agent can be easily integrate with blockchain systems and other tools. The agent is designed to be modular, allowing for easy extension and customization. The AgentKit agent is built uppon the Langchain framwork, which allows adding so called tools to the agent. These tools are responsible for performing specific tasks, such as interacting with blockchain systems, generating 3D models, and more.

### Agent Overview

Agent Logic: The agent's primary tasks are defined in agent.py, where different tools are invoked depending on the tasks assigned to the agent.
Modular Tools: Each agent is equipped with specific tools for tasks such as blockchain interactions, 3D model slicing, and more.

Available Tools
1. Blockchain Tools (tools/blockchain.py)

These tools are responsible for interacting with blockchain systems. They allow the agent to perform blockchain-related operations, such as interacting with smart contracts or performing transactions.

2. Keychain Generation Tools (tools/keychain_design_tools.py)

OpenAi's DALL-E model is used to generate keychain designs based on user input. The generated designs are then converted to STL files for 3D printing.

## API

Agents can be triggered via the /api routes in the API directory. The communication between the agents and the API allows users to interact with the system directly from a GUI app.

The server is built using FastAPI, a modern web framework for building APIs with Python 3.6+ based on standard Python type hints.

Once the server is running, you can send a POST request to the /api/get_gcode endpoint to generate G-code from an STL file.

## Setup
We recommend installing Poetry to manage dependencies. To install Poetry,  visit their docs: https://python-poetry.org/docs/

1. Clone the repository
2. Install dependencies using Poetry
```bash
poetry install
```
3. Run the agent server
```bash
poetry run python main.py
```
