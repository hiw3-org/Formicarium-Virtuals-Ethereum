require("dotenv").config();
const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const FormicariumModule = buildModule("FormicariumModule", (m) => {
  const usdc = process.env.USDC_ADDRESS;

  if (!usdc) {
    throw new Error("EXISTING_ERC20_ADDRESS is missing in .env file");
  }

  console.log(`Using existing USDC token at: ${usdc}`);

  // Deploy Formicarium Contract with the existing ERC20 token
  const formicarium = m.contract("Formicarium", [usdc]);

  return { formicarium };
});

module.exports = FormicariumModule;
