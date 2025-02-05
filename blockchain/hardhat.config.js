import "@nomicfoundation/hardhat-toolbox";
import dotenv from "dotenv";

dotenv.config();

export default {
  solidity: "0.8.28",
  networks: {
    baseSepolia: {
      url: `https://sepolia.base.org`, // Base Sepolia RPC
      accounts: [process.env.PRIVATE_KEY],
      chainId: 84532, // Base Sepolia chain ID
    },
    baseMain: {
      url: `https://mainnet.base.org`, // Base Sepolia RPC
      accounts: [process.env.PRIVATE_KEY],
      chainId: 8453, // Base Sepolia chain ID
    }
  },
};
