from web3 import Web3
import os
from dotenv import load_dotenv
import json
import asyncio
from langchain.tools import tool
import httpx

load_dotenv()

print(os.getenv("ADDRESS"))

# Determine the relative path to the G-code file
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../blockchain/artifacts/contracts/Formicarium.sol/"))
sc_file_path = os.path.join(base_path, "Formicarium.json")

# Load ABI from JSON file
with open(sc_file_path, "r") as file:
    contract_data = json.load(file)

# Extract ABI
abi = contract_data["abi"]

RPC_URL = "https://sepolia.base.org"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

contract_address = os.getenv("FORMICARIUM_TEST_ADDRESS")
printer_address = os.getenv("ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
address_2 = os.getenv("ADDRESS2")
private_key_2 = os.getenv("PRIVATE_KEY2")
contract = web3.eth.contract(address=contract_address, abi=abi)

@tool("sign_order", return_direct=True)
def sign_order(order_id):
    """Sign an order with the provided ID.

    Args:
        order_id (str): Order ID (Ethereum address) to be signed.
    """
    checksum_order_id = web3.to_checksum_address(order_id)
    
    try:
        # Get the nonce for the printer address
        nonce = web3.eth.get_transaction_count(printer_address)

        # Build the transaction
        tx = contract.functions.signOrder(checksum_order_id).build_transaction({
            'from': printer_address,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce
        })

        # Sign the transaction using the private key
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)

        # Log the signed transaction to inspect its attributes
        print(f"Signed transaction: {signed_tx}")

        # Send the raw transaction (convert to hex if necessary)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Print the transaction hash
        print(f"Order {checksum_order_id} signed! Transaction hash: {web3.to_hex(tx_hash)}")

        return web3.to_hex(tx_hash)  # Return the transaction hash for confirmation

    except Exception as e:
        print(f"Error signing order {checksum_order_id}: {e}")
        return f"Error signing order: {e}"

# Function to execute a new order
@tool("execute_new_order", return_direct=True)
def execute_new_order():
    """Execute a new order.
    """
    try:
        nonce = web3.eth.get_transaction_count(printer_address)
        tx = contract.functions.executeNewOrder().build_transaction({
            'from': printer_address,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"🚀 New order executed! Transaction hash: {web3.to_hex(tx_hash)}")

    except Exception as e:
        print(f"❌ Error executing new order: {e}")

# Function to complete an order as a provider
@tool("complete_order_provider", return_direct=True)
def complete_order_provider(order_id):
    """Complete an order as a provider.

    Args:
        order_id (_type_): _description_
    """
    checksum_order_id = web3.to_checksum_address(order_id)
    try:
        nonce = web3.eth.get_transaction_count(printer_address)
        tx = contract.functions.completeOrderProvider(checksum_order_id).build_transaction({
            'from': printer_address,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"✅ Order {checksum_order_id} completed! Transaction hash: {web3.to_hex(tx_hash)}")

    except Exception as e:
        print(f"❌ Error completing order {checksum_order_id}: {e}")

# Function to transfer funds to the provider
@tool("transfer_funds_provider", return_direct=True)
def transfer_funds_provider(order_id):
    """Transfer funds to the provider.

    Args:
        order_id (_type_): _description_
    """
    try:
        nonce = web3.eth.get_transaction_count(printer_address)
        tx = contract.functions.transferFundsProivder(order_id).build_transaction({
            'from': printer_address,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"💰 Funds transferred for order {order_id}! Transaction hash: {web3.to_hex(tx_hash)}")

    except Exception as e:
        print(f"❌ Error transferring funds for order {order_id}: {e}")
        
        
@tool("get_active_orders")
def get_active_orders():
    """Retrieve the list of active orders for the current provider address."""
    try:
        # Call the getActiveOrders function in the contract
        active_orders = contract.functions.getActiveOrders().call({
            'from': printer_address  # Set the msg.sender in Solidity
        })
        
        # Process and return the orders
        if active_orders:
            return active_orders
        else:
            return []
    
    except Exception as e:
        print(f"Error fetching active orders for provider {printer_address}: {e}")
        return []

# Event Handler
async def handle_event(event):
    if event.event == "OrderCreated":
        # SPROŽIMO POSTOPEK PODPISA NAROČILA
            # - Prvo pogledamo ali parametri naročila ustrezajo (enako kot pri API klicu)
            # - Podpišemo na SC
        if event['args']['printerId'] == printer_address:
            prompt = f"[Event trigger], OrderCreated: {event['args']}"
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8080/api/create_order_request", json={"prompt": prompt})
            if response.status_code != 200:
                print(f"Error processing chat request: {response.text}")
                return
            
    if event.event == "OrderStarted":
        if event['args']['printerId'] == printer_address:
            prompt = f"[Event trigger], OrderStarted: {event['args']}"
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8080/api/create_order_request", json={"prompt": prompt})
            if response.status_code != 200:
                print(f"Error processing chat request: {response.text}")
                return
            # SPROŽIMO POSTOPEK TISKANJA
            # - Najdemo Gkodo
            # - Pošljemo Gkodo na printer
            # - Poženemo tiskanje


# async def listen_events():
#     print("Listening for events...")

#     latest_block = web3.eth.get_block('latest')["number"]

#     while True:
#         try:

#             # Get new logs from the latest block
#             new_logs = web3.eth.get_logs({
#                 "fromBlock": latest_block,
#                 "address": contract_address
#             })

#             # Check if new_logs is None
#             if new_logs is None:
#                 print("No logs returned")
#                 continue  # Skip this iteration

#             # Process the logs
#             for log in new_logs:
#                 # Check the event signature by matching the topic
#                 # First, try to decode for OrderCreated
               
#                 if log["topics"][0].hex() == web3.keccak(text="OrderCreated(address,address,uint256,uint256,uint256)").hex():
#                     event_data = contract.events.OrderCreated().process_log(log)
#                     await handle_event(event_data)

#                 # Next, check for OrderStarted
#                 elif log["topics"][0].hex() == web3.keccak(text="OrderStarted(address,address)").hex():
#                     event_data = contract.events.OrderStarted().process_log(log)
#                     await handle_event(event_data)

#             latest_block = web3.eth.get_block('latest')["number"] + 1  # Move to the next block

#         except Exception as e:
#             print(f"Error fetching events: {e}")

#         await asyncio.sleep(1)  # Avoid excessive polling
        
        
async def listen_events():
    print("Listening for events...")

    latest_block = web3.eth.get_block('latest')["number"]

    while True:
        try:

            # Get new logs from the latest block
            new_logs = web3.eth.get_logs({
                "fromBlock": latest_block,
                "address": contract_address
            })

            # Check if new_logs is None
            if new_logs is None:
                print("No logs returned")
                continue  # Skip this iteration

            # Process the logs
            for log in new_logs:               
                # event_data = contract.events.OrderCreated().process_log(log)
                prompt = f"[Event trigger], blockchain: {log}"
                async with httpx.AsyncClient() as client:
                    response = await client.post("http://localhost:8080/api/create_order_request", json={"prompt": prompt})
                if response.status_code != 200:
                    print(f"Error processing chat request: {response.text}")
                    return

            latest_block = web3.eth.get_block('latest')["number"] + 1  # Move to the next block

        except Exception as e:
            print(f"Error fetching events: {e}")

        await asyncio.sleep(1)  # Avoid excessive polling



# # Run Listener
# async def reconnect():
#     while True:
#         try:
#             await listen_events()
#         except Exception as e:
#             print(f"WebSocket connection lost: {e}. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)


# asyncio.run(reconnect())
