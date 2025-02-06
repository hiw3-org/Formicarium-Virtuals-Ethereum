require("dotenv").config();
const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const FormicariumModule = buildModule("FormicariumModule", (m) => {
  
  const walletAddress = process.env.ADDRESS; // Load wallet from .env

  if (!walletAddress) {
    throw new Error("WALLET_ADDRESS is missing in .env file");
  }

  console.log(`Minting initial tokens to: ${walletAddress}`);

  // Deploy Mock ERC20 Token with 1 Million MTK tokens minted to `walletAddress`
  const paymentToken = m.contract("ERC20Mock", ["MockToken", "MTK", walletAddress, ethers.parseEther("1000000")]);

  // Deploy Formicarium Contract (depends on ERC20 token)
  const formicarium = m.contract("Formicarium", [paymentToken]);

  return { paymentToken, formicarium };
});

module.exports = FormicariumModule;