import Web3 from "web3";
import contractABI from "./Formicarium.json"; // Import ABI
import contractERC20ABI from "@openzeppelin/contracts/build/contracts/ERC20.json"; // Import ERC20 ABI

const RPC_URL = "https://sepolia.base.org"; // Base Sepolia RPC URL
const CONTRACT_ADDRESS = "0xa68d23AfC79A9acF2773a2dDd24412eDdf6E13d7"; // Replace with your contract address
const CONTRACT_ERC20_ADDRESS = "0x02BA94d06E5C9e6B7DB18eD80c475447939907b1";

// Initialize Web3 provider
const web3 = new Web3(window.ethereum); // Use MetaMask provider

// Function to load contract (Read-only)
export function getContract() {
    return new web3.eth.Contract(contractABI.abi, CONTRACT_ADDRESS);
}

// Function to load ERC20 contract (Read-only)
export function getERC20Contract() {
    return new web3.eth.Contract(contractERC20ABI.abi, CONTRACT_ERC20_ADDRESS);
}

// ✅ Function to fetch the contract owner
export async function fetchContractOwner() {
    try {
        const contract = getContract();
        const owner = await contract.methods.owner().call();
        return owner;
    } catch (error) {
        console.error("Error fetching contract data:", error);
        return null;
    }
}

// ✅ Function to fetch orders (from the connected MetaMask address)
export async function fetchOrders(address:string) {
    try {
        const contract = getContract();
        console.log("Fetching orders from address:", address);
        const orders = await contract.methods.getYourOrders().call({ from: address });
        console.log(orders);
        return orders;
    } catch (error) {
        console.log("Error fetching orders data", error);
    }
}

// ✅ Function to fetch printers (read-only)
export async function fetchPrinters() {
    try {
        const contract = getContract();
        const printers = await contract.methods.getAllPrinters().call();
        console.log(printers);
        return printers;
    } catch (error) {
        console.log("Error fetching printer data", error);
    }
}

// ✅ Function to fetch ETH balance of a MetaMask address
export async function fetchBalanceETH(address) {
    try {
        if (!address) return null;
        const balanceWei = await web3.eth.getBalance(address);
        return web3.utils.fromWei(balanceWei, "ether"); // Convert from Wei to ETH
    } catch (error) {
        console.error("Error fetching ETH balance:", error);
        return null;
    }
}

export async function fetchBalanceERC20(address: string): Promise<number | null> {
    try {
        if (!address) return null;

        const contract = getERC20Contract();
        const balance: bigint | string = await contract.methods.balanceOf(address).call();

        // ✅ Ensure `balance` is properly converted
        return Number(web3.utils.fromWei(balance.toString(), "ether"));
    } catch (error) {
        console.error("Error fetching ERC20 balance:", error);
        return null;
    }
}

// ✅ Function to post an order using MetaMask account
export async function placeOrder(address:string ,orderID:string, printerID:string, minPrice:number, actualPrice:number, duration:number) {
    try {
        const contract = getContract();
        const minPriceInt = (minPrice*1e18).toFixed(0);
        const actualPriceInt = (actualPrice*1e18).toFixed(0);
        const orderDurationSeconds = (duration * 3600).toFixed(0); // Convert minutes to seconds


        //Approve to spend ERC20 tokens
        const erc20Contract = getERC20Contract();
        const approveTx = await erc20Contract.methods.approve(CONTRACT_ADDRESS, actualPriceInt).send({ from: address });
        console.log("Approved to spend ERC20 tokens:", approveTx.transactionHash);

        console.log("Posting order from address:", address);
        const tx = await contract.methods.createOrder(orderID, printerID, minPriceInt, actualPriceInt, orderDurationSeconds).send({ from: address });

        console.log("Transaction hash:", tx.transactionHash);
        return tx.transactionHash;
    } catch (error) {
        console.log("Error sending order data", error);
    }
}
