require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const recipient = process.env.ADDRESS2;
    const mockERC20Address = process.env.ERC_ADDRESS;
    const deployerPrivateKey = process.env.PRIVATE_KEY;

    if (!recipient || !mockERC20Address || !deployerPrivateKey) {
        throw new Error("Missing environment variables! Ensure DEPLOYER_PRIVATE_KEY, NEW_ACCOUNT_ADDRESS, and MOCK_ERC20_ADDRESS are set in .env");
    }

    // Load Deployer Account from Private Key
    const provider = hre.ethers.provider;
    const deployer = new hre.ethers.Wallet(deployerPrivateKey, provider);

    console.log(`Using deployer account: ${deployer.address}`);

    // STEP 1: Transfer ETH to recipient
    console.log(`Sending 0.001 ETH to: ${recipient} for gas fees...`);
    const ethTx = await deployer.sendTransaction({
        to: recipient,
        value: hre.ethers.parseEther("0.001"), // Amount of ETH to send
    });
    await ethTx.wait();
    console.log(`✅ ETH Transfer successful! Tx Hash: ${ethTx.hash}`);

    // STEP 2: Transfer ERC20 Mock Tokens to recipient
    const paymentToken = await hre.ethers.getContractAt("ERC20Mock", mockERC20Address, deployer);
    console.log(`Sending 100 MTK tokens to: ${recipient}...`);

    const tokenTx = await paymentToken.transfer(recipient, hre.ethers.parseEther("100"));
    await tokenTx.wait();
    console.log(`✅ Token Transfer successful! Tx Hash: ${tokenTx.hash}`);

    // STEP 3: Verify Final Balances
    const ethBalance = await provider.getBalance(recipient);
    const tokenBalance = await paymentToken.balanceOf(recipient);

    console.log(`🎯 Final Balances of ${recipient}:`);
    console.log(`   ETH: ${hre.ethers.formatEther(ethBalance)} ETH`);
    console.log(`   MTK: ${hre.ethers.formatEther(tokenBalance)} MTK`);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
