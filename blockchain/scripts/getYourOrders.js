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

    // Get users orders
    const orders = await formicarium.getYourOrders();
    console.log(`📌 Found ${orders.length} orders.`);
    console.log(orders);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});

