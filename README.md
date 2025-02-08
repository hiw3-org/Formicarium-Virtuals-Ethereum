![Formicarium Logo](assets/banner.png)

# Formicarium

Formicarium is a decentralized platform where an AI agent coordinates a fleet of autonomous machines and robots to manufacture customized products. This system integrates AI-driven user interactions with a blockchain-based marketplace, allowing users to seamlessly request and receive 3D-printed products.

## Features

- AI-driven Customization: Users interact with an AI agent (developed with CDP AgentKit) via a chat interface to define their product specifications.
- 2D to 3D Model Conversion: AI generates a 2D rendering of the requested design and an STL file for 3D printing.
- Decentralized Marketplace: Smart contracts facilitate transactions between users and autonomous manufacturing machines.
- Blockchain-powered Transactions: Customers lock funds in USDC tokens, ensuring secure and trustless service execution.
- Optimized Order Execution: Machines evaluate price and queue positions, enabling users to accelerate order processing by providing additional funds.
- Real-time Order Tracking: Customers can monitor their orders, including livestreams of their products being manufactured.

## How It Works

1. User Interaction: Customers describe their desired product to the AI agent via chat.
2. AI Processing: The AI generates a 2D rendering and an STL file for 3D printing. STL code is transformed into G-code for the 3D printer.
3. Marketplace Engagement: Smart contracts manage the bidding and agreement process between users and service providers.
4. Manufacturing Execution: The autonomous 3D printer utlizies G-code for printing ordered products.
5. Order Tracking: Users can monitor the order status and view a live feed of the printing process.
6. Payment Release: Upon successful order completion, locked funds are released to the service provider.

### Prerequisites

- Node.js & npm
- Python 3.9+
- Hardhat
- FastAPI
- Next.js
- OctoPrint
- AgentKit
