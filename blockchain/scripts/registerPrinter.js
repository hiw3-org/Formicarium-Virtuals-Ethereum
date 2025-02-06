require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const formicariumAddress = process.env.FORMICARIUM_TEST_ADDRESS;
    const deployerPrivateKey = process.env.PRIVATE_KEY;

    if (!formicariumAddress || !deployerPrivateKey) {
        throw new Error("FORMICARIUM_ADDRESS, NEW_PRINTER_ADDRESS, or DEPLOYER_PRIVATE_KEY is missing in .env file");
    }

    // Connect to the blockchain using the deployer's private key
    const provider = hre.ethers.provider;
    const deployer = new hre.ethers.Wallet(deployerPrivateKey, provider);

    console.log(`Using deployer account: ${deployer.address}`);

    // Load the Formicarium contract
    const formicarium = await hre.ethers.getContractAt("Formicarium", formicariumAddress, deployer);

    // Register the printer with a JSON string as details
    const printerDetails = JSON.stringify({
        model: "PrusaMK3S",
        location: "Berlin, Germany",
        API: "localhost:3000",
    });

    console.log(`Sending transaction to register printer: ${printerDetails}`);
    const tx = await formicarium.connect(deployer).registerPrinter(printerDetails);
    await tx.wait();

    console.log(`✅ Printer registered successfully!`);

    // Verify registration
    const printerData = await formicarium.printers(deployer.address);
    console.log(`🎯 Registered Printer Info:`, printerData);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
