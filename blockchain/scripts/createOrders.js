require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const formicariumAddress = process.env.FORMICARIUM_TEST_ADDRESS;
    const erc20Address = process.env.ERC_ADDRESS;
    const deployerPrivateKey = process.env.PRIVATE_KEY;
    const customerAddress = process.env.ADDRESS;

    if (!formicariumAddress || !erc20Address || !deployerPrivateKey || !customerAddress) {
        throw new Error("Missing environment variables! Ensure FORMICARIUM_ADDRESS, EXISTING_ERC20_ADDRESS, DEPLOYER_PRIVATE_KEY, and CUSTOMER_ADDRESS are set in .env file");
    }

    // Connect to the blockchain using the deployer's private key
    const provider = hre.ethers.provider;
    const deployer = new hre.ethers.Wallet(deployerPrivateKey, provider);

    console.log(`Using deployer account: ${deployer.address}`);

    // Load the Formicarium contract
    const formicarium = await hre.ethers.getContractAt("Formicarium", formicariumAddress, deployer);

    // Load ERC20 token contract
    const paymentToken = await hre.ethers.getContractAt("IERC20", erc20Address, deployer);

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

    const N_orders = 5; // Number of orders per printer

    // Calculate the total amount needed for approval
    let totalAmountNeeded = hre.ethers.parseEther("0");
    for (let i = 0; i < printers.length; i++) {
        for (let j = 0; j < N_orders; j++) {
            const minimalPrice = 10; // 5-10 MTK
            const actualPrice = 2; // + 0-2 MTK
            totalAmountNeeded += actualPrice;
        }
    }

    // Check current allowance
    const currentAllowance = await paymentToken.allowance(customerAddress, formicariumAddress);
    if (currentAllowance < totalAmountNeeded) {
        console.log(`⚠️ Approving ${hre.ethers.formatEther(totalAmountNeeded)} MTK for order payments...`);
        const approveTx = await paymentToken.connect(deployer).approve(formicariumAddress, totalAmountNeeded);
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
            const orderId = hre.ethers.Wallet.createRandom().address;
            const minimalPrice = hre.ethers.parseEther((Math.random() * 5 + 5).toFixed(2)); // 5-10 MTK
            const actualPrice = minimalPrice + hre.ethers.parseEther((Math.random() * 2).toFixed(2)); // + 0-2 MTK
            const duration = Math.floor(Math.random() * 86400) + 3600; // 1 hour to 1 day

            console.log(`📌 Creating order ${orderId} for printer ${printerId}`);
            console.log(`🏷️ Minimal Price: ${hre.ethers.formatEther(minimalPrice)} MTK`);
            console.log(`🏷️ Actual Price: ${hre.ethers.formatEther(actualPrice)} MTK`);
            console.log(`⏳ Duration: ${duration} seconds`);

            // Create the order
            const tx = await formicarium.connect(deployer).createOrder(orderId, printerId, minimalPrice, actualPrice, duration);
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

