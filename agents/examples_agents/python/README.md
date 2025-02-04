# Formicarium - Agentkit Langchain Chatbot Python Example

This example demonstrates an agent setup as a terminal style chatbot with access to the full set of CDP Agentkit actions.

We can add server functionality to this chatbot to make it a full-fledged agent for the frontend. This chatbot is a simple example of how to interact with the CDP Agentkit using the Python SDK.

## Requirements
- Python 3.10+ (3.12 works for me, 3.13 did not work, some packages do not support it yet)
- Poetry for package management and tooling
  - [Poetry Installation Instructions](https://python-poetry.org/docs/#installation)
    * This is basically pip on steroids, it streamlines the process of managing dependencies and virtual environments
- Make
  - [Make for Windows](https://community.chocolatey.org/packages/make)
    * Not really necessary, you can run the commands manually
- [CDP API Key](https://portal.cdp.coinbase.com/access/api)
  * When pasting the private API key in .env file, leave everything in, like this CDP_API_KEY_PRIVATE_KEY=-----BEGIN EC PRIVATE KEY-----\nMHcC...... 
  * Remove .example from .env.example and fill in the values
- [OpenAI API Key](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)


## Ask the chatbot to engage in the Web3 ecosystem!
- "Transfer a portion of your ETH to john2879.base.eth"
- "Deploy an NFT that will go super viral!"
- "Choose a name for yourself and register a Basename for your wallet"
- "Deploy an ERC-20 token with total supply 1 billion"

## Installation
```bash
poetry config virtualenvs.in-project true
poetry install
```
## Run the Chatbot

```bash
make run
```

or 

**Chatbot cli** 
```bash
poetry run python chatbot.py
```

**Chatbot server**
```bash
poetry run python .\chatbot-server.py
```
