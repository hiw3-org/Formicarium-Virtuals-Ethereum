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
contract = web3.eth.contract(address=contract_address, abi=abi)

@tool("sign_order", return_direct=True)
def sign_order(order_id):
    """SIgn an order with the provided ID.

    Args:
        order_id (_type_): _description_
    """
    try:
        nonce = web3.eth.get_transaction_count(printer_address)
        tx = contract.functions.signOrder(order_id).build_transaction({
            'from': printer_address,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"Order {order_id} signed! Transaction hash: {web3.to_hex(tx_hash)}")

    except Exception as e:
        print(f"Error signing order {order_id}: {e}")

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
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

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
    try:
        nonce = web3.eth.get_transaction_count(printer_address)
        tx = contract.functions.completeOrderProvider(order_id).build_transaction({
            'from': printer_address,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"✅ Order {order_id} completed! Transaction hash: {web3.to_hex(tx_hash)}")

    except Exception as e:
        print(f"❌ Error completing order {order_id}: {e}")

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
        
        
@tool("get_provider_orders", return_direct=True)
def get_provider_orders():
    """Retrieve the list of orders for a given provider address from the providerOrders mapping.

    Args:
        provider_address (str): The address of the provider to check orders for.

    Returns:
        List of orders associated with the given provider address.
    """
    try:
        # Call the providerOrders mapping to get the list of orders for the given provider address
        provider_orders = contract.functions.providerOrders(os.getenv("ADDRESS")).call()

        if provider_orders:
            return provider_orders
        else:
            return []

    except Exception as e:
        print(f"Error fetching orders for provider {os.getenv("ADDRESS")}: {e}")
        return []

# Event Handler
async def handle_event(event):
    if event['event'] == "OrderCreated":
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
            
    
    elif event['event'] == "OrderStarted":
        if event['args']['printerId'] == printer_address:
            print(f"Arguments: {event['args']}")
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
                event_data = contract.events.OrderCreated().process_log(log)
                await handle_event(event_data)

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
