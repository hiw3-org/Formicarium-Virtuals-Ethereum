import { ethers } from "ethers";
import contractABI from "./Formicarium.json"; // Import ABI
import contractERC20ABI from "@openzeppelin/contracts/build/contracts/ERC20.json"; // Import ABI

const RPC_URL = "https://sepolia.base.org"; // Base Sepolia RPC URL
const CONTRACT_ADDRESS = "0xa68d23AfC79A9acF2773a2dDd24412eDdf6E13d7"; // Replace with your contract address

const CONTRACT_ERC20_ADDRESS = "0x02BA94d06E5C9e6B7DB18eD80c475447939907b1";

const provider = new ethers.JsonRpcProvider(RPC_URL);

// Function to load contract
export function getContract() {
    return new ethers.Contract(CONTRACT_ADDRESS, contractABI.abi, provider);
}

export function getERC20Contract() {
    return new ethers.Contract(CONTRACT_ERC20_ADDRESS, contractERC20ABI.abi, provider);
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

export async function fetchBalanceETH(address:string | null ) {
    try {
        if(!address) return null;
        const balance = await provider.getBalance(address);
        return balance;
    } catch (error) {
        console.error("Error fetching ETH balance:", error);
        return null;
    }
}

export async function fetchBalanceERC20(address:string | null ) {
    try {
        if(!address) return null;
        const contract = getERC20Contract();
        const balance = await contract.balanceOf(address);
        return balance;
    } catch (error) {
        console.error("Error fetching ERC20 balance:", error);
        return null;
    }
}

// export async function sendOrder(orderId : string, address printerId){
//     try {
//         const contract =getContract();
//         const tx = await contract.createOrder(orderData)
//         await tx.wait();
//         return tx.hash;
//     }catch (error) {
//         console.log("Error sending order data", error);
//
//     }
// }
