require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const formicariumAddress = process.env.FORMICARIUM_TEST_ADDRESS;
    const printerPrivateKey = process.env.PRIVATE_KEY;
    const printerAddress = process.env.ADDRESS;

    if (!formicariumAddress || !printerPrivateKey || !printerAddress) {
        throw new Error("Missing environment variables! Ensure FORMICARIUM_TEST_ADDRESS, PRINTER_PRIVATE_KEY, and PRINTER_ADDRESS are set in .env file");
    }

    // Connect to the blockchain using the printer's private key
    const provider = hre.ethers.provider;
    const printer = new hre.ethers.Wallet(printerPrivateKey, provider);

    console.log(`Using printer account: ${printer.address}`);

    // Load the Formicarium contract
    const formicarium = await hre.ethers.getContractAt("Formicarium", formicariumAddress, printer);

    // Fetch all orders assigned to this provider
    console.log("🔄 Fetching provider's orders...");
    const orderIds = await formicarium.getProviderOrders(printerAddress);

    if (orderIds.length === 0) {
        console.log("⚠️ No active orders found for this provider. Exiting...");
        return;
    }

    console.log(`📌 Found ${orderIds.length} orders. Checking which need execution and completion...`);

    for (let orderId of orderIds) {
        const orderData = await formicarium.orders(orderId);

        // Destructure order details
        const {
            startTime,
            isSigned,
            isCompletedProvider
        } = orderData;

        // **Step 1: Execute the first unsigned order**
        if (isSigned && !isCompletedProvider && Number(startTime) === 0) {
            console.log(`🚀 There exist an active order`);
            try {
                const tx = await formicarium.connect(printer).executeNewOrder();
                await tx.wait();
                console.log(`✅ New order is being executed!`);
            } catch (error) {
                console.error(`❌ Failed to execute order ${orderId}:`, error.message);
            }
            return; // Stop script after executing one order
        }        
    }

    console.log("🎯 No orders were executed this run.");
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
