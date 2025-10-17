![Formicarium Logo](assets/banner.png)

---

> ### 🚀 **NEW in v2.0: ERC-8004 Integration**
> 
> Formicarium now integrates with **[ERC-8004 (Trustless Agents Standard)](https://eips.ethereum.org/EIPS/eip-8004)** for decentralized agent identity and reputation management. Our AI agents are registered on-chain with verifiable identities, and all customer feedback is permanently recorded on the blockchain, ensuring **transparency and trust** in autonomous service delivery.
---

# Formicarium

Formicarium is a decentralized platform where an AI agent coordinates a fleet of autonomous machines and robots to manufacture customized products. This system integrates AI-driven user interactions with a blockchain-based marketplace, allowing users to seamlessly request and receive 3D-printed products.

## Features

- AI-driven Customization: Users interact with an AI agent (developed with CDP AgentKit) via a chat interface to define their product specifications.
- 2D to 3D Model Conversion: AI generates a 2D rendering of the requested design and an STL file for 3D printing.
- Decentralized Marketplace: Smart contracts facilitate transactions between users and autonomous manufacturing machines.
- **ERC-8004 Integration**: Agents are registered on-chain with verifiable identities and reputation tracking via the Trustless Agents Standard.
- Blockchain-powered Transactions: Customers lock funds in USDC tokens, ensuring secure and trustless service execution.
- Optimized Order Execution: Machines evaluate price and queue positions, enabling users to accelerate order processing by providing additional funds.
- Real-time Order Tracking: Customers can monitor their orders, including livestreams of their products being manufactured.
- **On-chain Reputation System**: Customer feedback is cryptographically signed and stored on-chain, building transparent agent reputation scores.

## How It Works

1. User Interaction: Customers describe their desired product to the AI agent via chat.
2. AI Processing: The AI generates a 2D rendering and an STL file for 3D printing. STL code is transformed into G-code for the 3D printer.
3. Marketplace Engagement: Smart contracts manage the bidding and agreement process between users and service providers.
4. Manufacturing Execution: The autonomous 3D printer utlizies G-code for printing ordered products.
5. Order Tracking: Users can monitor the order status and view a live feed of the printing process.
6. Payment Release: Upon successful order completion, locked funds are released to the service provider.

## ERC-8004 Integration: Trustless Agent Identity & Reputation

Formicarium v2.0 implements the [ERC-8004 Trustless Agents Standard](https://eips.ethereum.org/EIPS/eip-8004), providing decentralized identity and reputation management for our autonomous AI agents. This integration ensures transparency, accountability, and trust in agent-to-customer interactions.


### Integration Flow

#### 1. **Agent Registration** (One-time setup)

Both Design and Hardware agents register their on-chain identities:

```
Agent Registration → ERC-8004 Identity Registry → Receive Agent ID (NFT)
```

Each agent's registration includes:
- Name, description, and endpoints
- Wallet address
- HTTP API endpoint
- Supported trust mechanisms (reputation)


#### 2. **Order Processing** (Formicarium Contract)

Orders are processed through the Formicarium marketplace contract as before:

```
1. Customer creates order (locks USDC)
2. Design Agent generates 3D model
3. Hardware Agent executes 3D printing
4. Customer receives product
5. Funds released to Hardware Agent
```

#### 3. **Feedback Authorization** (Cryptographic Trust)

After order completion, the Hardware Agent creates a cryptographically signed feedback authorization:

```
┌─────────────────────────────────────────────────────────────┐
│  Hardware Agent (Agent ID 25)                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Creates FeedbackAuth:                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • agentId: 25                                      │    │
│  │ • clientAddress: 0xe880...7310                     │    │
│  │ • indexLimit: 1                                    │    │
│  │ • expiry: timestamp + 1 week                       │    │
│  │ • chainId: 84532 (Base Sepolia)                    │    │
│  │ • signature: EIP-191 signed by agent's wallet     │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│              Sends to Design Agent via API                  │
└─────────────────────────────────────────────────────────────┘
```

This ensures:
- Only the Hardware Agent can authorize feedback
- Only the specified customer can submit feedback
- Feedback authorization has a time limit
- Everything is cryptographically verifiable

#### 4. **Feedback Submission** (On-chain Reputation)

Design Agent prompts the customer for feedback and submits it to the ERC-8004 Reputation Registry:

```
┌─────────────────────────────────────────────────────────────┐
│  Design Agent (Agent ID 26)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Receives FeedbackAuth from Hardware Agent               │
│  2. Prompts Customer: "Please rate the service (0-100)"     │
│  3. Customer provides: Score, Tags                          │
│                                                             │
│  Submits to ERC-8004 Reputation Registry:                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • agentId: 25 (Hardware Agent)                     │    │
│  │ • score: 85/100 (from customer)                    │    │
│  │ • tag1: "quality"                                  │    │
│  │ • tag2: "speed"                                    │    │
│  │ • fileURI: "ipfs://Qm..."                          │    │
│  │ • feedbackAuth: <signed authorization>            │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│      Permanently stored on-chain for Hardware Agent        │
└─────────────────────────────────────────────────────────────┘
```

**Flow Summary:**
1. Customer interacts with Design Agent throughout the process
2. Hardware Agent completes the printing service
3. Hardware Agent signs feedback authorization for the customer's address
4. Hardware Agent sends authorization to Design Agent
5. Design Agent prompts customer to rate the Hardware Agent's service
6. Design Agent submits feedback on-chain using the authorization
7. Feedback is permanently recorded for Hardware Agent's reputation

### Deployment Evidence (Base Sepolia Testnet)

#### Registered Agents

| Agent | ID | Owner Address | Registration TX |
|-------|----|--------------|-----------------| 
| Hardware Agent | 25 | `0xf4b2...7760` | [View on BaseScan](https://sepolia.basescan.org/tx/0x69ee0529d51ca5a9c277ac1bbf73d3cff3039645fa4d5b74a71d5680db2279b3) |
| Design Agent | 26 | `0xe880...7310` | [View on BaseScan](https://sepolia.basescan.org/tx/0x84276a7cdd1a20a3a075a0e3ca0b6471768719296fe620cffa4493a75325b8a9) |

#### Feedback Submission

| Parameter | Value |
|-----------|-------|
| Agent ID | 25 (Hardware Agent) |
| Customer | `0xe880...7310` |
| Score | 85/100 |
| Tags | quality, speed |
| Transaction | [View on BaseScan](https://sepolia.basescan.org/tx/0x9ef0ec72f5d252b588b4b4105ec0202ab1de1dd385d895025bd7620898facd6c) |
| Block | 32483273 |
| Status | ✅ Verified |
| Revoked | No |

#### ERC-8004 Contracts (Base Sepolia)

| Contract | Address | Purpose |
|----------|---------|---------|
| Identity Registry | `0x7177a6867296406881E20d6647232314736Dd09A` | Agent registration & identity |
| Reputation Registry | `0xB5048e3ef1DA4E04deB6f7d0423D06F63869e322` | Feedback & reputation tracking |

### Benefits of ERC-8004 Integration

1. **Decentralized Identity**: Agents have verifiable on-chain identities (NFTs) that cannot be spoofed
2. **Transparent Reputation**: All feedback is public and immutable, building trust through transparency
3. **Cryptographic Authorization**: Only authorized parties can submit feedback, preventing spam/manipulation
4. **Cross-Platform Compatibility**: Agent identities work across any ERC-8004 compatible platform
5. **Permissionless Trust**: No central authority needed - trust is built through verifiable on-chain history

### Technical Implementation

The integration is implemented in:
- `blockchain/scripts/registerAgentERC8004.js` - Agent registration script
- `blockchain/scripts/submitFeedbackERC8004.js` - Two-step feedback process
- `hardware/agent_ai/blockchain_tools.py` - Hardware agent feedback tools
- `blockchain/test/ERC8004.test.js` - Comprehensive test suite

For detailed implementation, see the [blockchain tests](blockchain/test/ERC8004.test.js).

### Prerequisites

- Node.js & npm
- Python 3.9+
- Hardhat
- FastAPI
- Next.js
- OctoPrint
- AgentKit
