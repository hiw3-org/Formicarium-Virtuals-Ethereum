require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const formicariumAddress = process.env.FORMICARIUM_TEST_ADDRESS;
    const erc20Address = process.env.ERC_ADDRESS;
    const customerPrivateKey = process.env.PRIVATE_KEY2;
    const customerAddress = process.env.ADDRESS2;

    if (!formicariumAddress || !erc20Address || !customerPrivateKey || !customerAddress) {
        throw new Error("Missing environment variables! Ensure FORMICARIUM_ADDRESS, EXISTING_ERC20_ADDRESS, CUSTOMER_PRIVATE_KEY, and CUSTOMER_ADDRESS are set in .env file");
    }

    // Connect to the blockchain using the customer's private key
    const provider = hre.ethers.provider;
    const customer = new hre.ethers.Wallet(customerPrivateKey, provider);

    console.log(`Using customer account: ${customer.address}`);

    // Load the Formicarium contract
    const formicarium = await hre.ethers.getContractAt("Formicarium", formicariumAddress, customer);

    // Load ERC20 token contract
    const paymentToken = await hre.ethers.getContractAt("IERC20", erc20Address, customer);

    // Fetch all printers from `getAllPrinters()`
    console.log("🔄 Fetching registered printers...");
    const printers = await formicarium.getAllPrinters();

    if (printers.length === 0) {
        console.log("⚠️ No registered printers found. Exiting...");
        return;
    }

    console.log(`📌 Found ${printers.length} printers. Preparing to create orders...`);


    // Ensure customer has enough tokens
    const balance = await paymentToken.balanceOf(customerAddress);
    console.log(`💰 Customer Balance: ${hre.ethers.formatEther(balance)} MTK`);

    const N_orders = 1; // Number of orders per printer

    // Calculate the total amount needed for approval
    // Calculate the total amount needed for approval
    let totalAmountNeeded = hre.ethers.parseEther("0");

    for (let i = 0; i < printers.length; i++) {
        for (let j = 0; j < N_orders; j++) {
            const minimalPrice = hre.ethers.parseEther("10"); // Convert to BigInt
            const actualPrice = minimalPrice + hre.ethers.parseEther("2"); // Convert to BigInt
            totalAmountNeeded = totalAmountNeeded + actualPrice; // Ensure same type
        }
    }

    console.log(`🔍 Total allowance needed: ${hre.ethers.formatEther(totalAmountNeeded)}`);

    // Check current allowance
    const currentAllowance = await paymentToken.allowance(customerAddress, formicariumAddress);
    if (currentAllowance < totalAmountNeeded) {
        console.log(`⚠️ Approving ${hre.ethers.formatEther(totalAmountNeeded)} MTK for order payments...`);
        const approveTx = await paymentToken.connect(customer).approve(formicariumAddress, totalAmountNeeded);
        await approveTx.wait();
    } else {
        console.log("✅ Sufficient allowance already set.");
    }

    // Create orders for each printer
    for (let printer of printers) {
        for (let i = 0; i < N_orders; i++) {
            const printerId = printer.ID;
            console.log(`📌 Found printer: ${printerId} | Details: ${printer.printerDetails}`);

            // Generate unique order ID
            const orderId = "0x83a2b91cfd4c8b84c6ebd901052ec05c82185394";
            const minimalPrice = hre.ethers.parseEther((Math.random() * 5 + 5).toFixed(2)); // 5-10 MTK
            const actualPrice = minimalPrice + hre.ethers.parseEther((Math.random() * 2).toFixed(2)); // + 0-2 MTK
            // const duration = Math.floor(Math.random() * 86400) + 3600; // 1 hour to 1 day
            const duration = 777;

            console.log(`📌 Creating order ${orderId} for printer ${printerId}`);
            console.log(`🏷️ Minimal Price: ${hre.ethers.formatEther(minimalPrice)} MTK`);
            console.log(`🏷️ Actual Price: ${hre.ethers.formatEther(actualPrice)} MTK`);
            console.log(`⏳ Duration: ${duration} seconds`);

            // Create the order
            const tx = await formicarium.connect(customer).createOrder(orderId, printerId, minimalPrice, actualPrice, duration);
            await tx.wait();
            console.log(`✅ Order ${orderId} created successfully!`);
        }
    }

    console.log(`🎯 Successfully created ${printers.length * N_orders} orders.`);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});

