require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const formicariumAddress = process.env.FORMICARIUM_TEST_ADDRESS;
    const erc20Address = process.env.ERC_ADDRESS;
    const printerPrivateKey = process.env.PRIVATE_KEY;
    const printerAddress = process.env.ADDRESS;

    if (!formicariumAddress || !erc20Address || !printerPrivateKey || !printerAddress) {
        throw new Error("Missing environment variables! Ensure FORMICARIUM_ADDRESS, EXISTING_ERC20_ADDRESS, PRINTER_PRIVATE_KEY, and PRINTER_ADDRESS are set in .env file");
    }

    // Connect to the blockchain using the printer's private key
    const provider = hre.ethers.provider;
    const printer = new hre.ethers.Wallet(printerPrivateKey, provider);

    console.log(`Using printer account: ${printer.address}`);

    // Load the Formicarium contract
    const formicarium = await hre.ethers.getContractAt("Formicarium", formicariumAddress, printer);

    // Fetch all order IDs for this printer from the new getter function
    console.log("🔄 Fetching provider orders...");
    const orderIds = await formicarium.getProviderOrders(printerAddress);

    if (orderIds.length === 0) {
        console.log("⚠️ No orders found in providerOrders mapping. Exiting...");
        return;
    }

    console.log(`📌 Found ${orderIds.length} orders. Checking which need to be signed...`);

    // Sign all unsigned orders
    for (let orderId of orderIds) {
        // Fetch order details
        const order = await formicarium.orders(orderId);

        if (!order.isSigned) {
            console.log(`✍️ Signing order ${orderId}...`);

            try {
                const tx = await formicarium.connect(printer).signOrder(orderId);
                await tx.wait();
                console.log(`✅ Order ${orderId} signed successfully!`);
            } catch (error) {
                console.error(`❌ Failed to sign order ${orderId}:`, error.message);
            }
        } else {
            console.log(`🚫 Order ${orderId} is already signed. Skipping...`);
        }
    }

    console.log("🎯 All possible orders have been signed.");
}


main().catch((error) => {
    console.error(error);
    process.exit(1);
});

