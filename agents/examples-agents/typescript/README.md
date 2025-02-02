# CDP AgentKit Langchain Extension Examples - Chatbot Typescript

This example demonstrates an agent setup as a terminal style chatbot with access to the full set of CDP AgentKit actions.

## Requirements

- Node.js 18+
- [CDP API Key](https://portal.cdp.coinbase.com/access/api)
  * When pasting the private API key in .env file, leave everything in, like this CDP_API_KEY_PRIVATE_KEY=-----BEGIN EC PRIVATE KEY-----\nMHcC...... 
  * Remove .example from .env.example and fill in the values
- [OpenAI API Key](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)

### Checking Node Version

Before using the example, ensure that you have the correct version of Node.js installed. The example requires Node.js 18 or higher. You can check your Node version by running:

```bash
node --version
npm --version
```

## Installation

```bash
npm install
```

## Run the Chatbot

### Set ENV Vars

- Ensure the following ENV Vars are set:
  - "CDP_API_KEY_NAME"
  - "CDP_API_KEY_PRIVATE_KEY"
  - "OPENAI_API_KEY"
  - "NETWORK_ID" (Defaults to `base-sepolia`)

```bash
npm start
```

## License

Apache-2.0
