require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const walletAddress = process.env.ADDRESS;
    const mockERC20Address = process.env.ERC_ADDRESS;

    if (!walletAddress || !mockERC20Address) {
        console.error("WALLET_ADDRESS or MOCK_ERC20_ADDRESS is missing in .env file");
        process.exit(1);
    }

    const accounts = await hre.ethers.getSigners();
    const deployer = accounts[0]; // Use first signer (deployer)

    console.log(`Using deployer account: ${deployer.address}`);

    // Load ERC20 contract
    const paymentToken = await hre.ethers.getContractAt("ERC20Mock", mockERC20Address, deployer);

    console.log(`Minting tokens to: ${walletAddress}`);

    // Mint 1000 tokens
    const tx = await paymentToken.mint(walletAddress, hre.ethers.parseEther("1000"));
    await tx.wait();

    // Check the new balance
    const balance = await paymentToken.balanceOf(walletAddress);
    console.log(`New Balance of ${walletAddress}: ${hre.ethers.formatEther(balance)} MTK`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
