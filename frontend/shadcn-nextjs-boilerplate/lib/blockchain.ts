import { ethers } from "ethers";
import contractABI from "./Formicarium.json"; // Import ABI

const RPC_URL = "https://sepolia.base.org"; // Base Sepolia RPC URL
const CONTRACT_ADDRESS = "0x00DE21fa24Bd30aB7a22228FcB4Ab256191F4676"; // Replace with your contract address

const provider = new ethers.JsonRpcProvider(RPC_URL);

// Function to load contract
export function getContract() {
    return new ethers.Contract(CONTRACT_ADDRESS, contractABI.abi, provider);
}

// Example: Fetch contract owner (Modify based on your contract)
export async function fetchContractOwner() {
    try {
        const contract = getContract();
        const owner = await contract.owner(); // Assuming contract has an `owner()` function
        return owner;
    } catch (error) {
        console.error("Error fetching contract data:", error);
        return null;
    }
}

export async function fetchOrders(){
    try {
        const contract =getContract();
        const orders = await contract.getYourOrders()
        return orders;
    }catch (error) {
        console.log("Error fetching orders data", error);

    }
}

export async function fetchPrinters(){
    try {
        const contract =getContract();
        const printer = await contract.getAllPrinters()
        return printer;
    }catch (error) {
        console.log("Error fetching printer data", error);

    }
}
