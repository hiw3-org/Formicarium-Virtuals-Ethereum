# Formicarium - Hardware

This directory contains the core hardware agent code and its associated tools within the Formicarium framework.

## Overview
The hardware agent is responsible for tasks such as interacting with smart contracts, interfacing with OctoPrint for 3D printing management, and calculating the cost of 3D prints based on current electricity prices (he himself serached on the web). This agent is also built using the AgentKit framework, which allows seamless integration of various tools, providing flexibility and customization for hardware-related tasks.

### Tools

The hardware agent comes with several tools designed for specific tasks:
1. Blockchain Tools (blockchain_tools.py)

These tools allow the agent to interact with smart contracts. This includes operations such as reading new 3D print orders, signigng the orders, resolving the orders as finished and more.

2. OctoPrint Tools (octoprint_tools.py)

These tools allow the agent to interface with OctoPrint, a widely used 3D printer management software. The agent can monitor and control 3D printing jobs, retrieve printer status, and send commands to load gcode and start the printing proces.

3. Price Calculator Tools (calculator_tools.py)

This tool helps the agent calculate the cost of a 3D printing job based on the current electricity and filament price. The agent fetches live electricity price data from the web and computes the cost based on the printer's energy consumption and print duration. This tool ensures that the user can estimate the print cost in real-time, making it easy to determine the price before starting a print.

## API Integration

Just like the user agent, the hardware agent can be triggered via the /api routes in the API directory. The communication between the hardware agent and the API allows users to interact with the system directly through HTTP requests, making it easy to integrate with a larger application. The user agent can send requests to the hardware agent to perform tasks such as calculating print costs.


The FastAPI server handles these routes.

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
