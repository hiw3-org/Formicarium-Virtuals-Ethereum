from web3 import Web3
import os
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()

# Load ABI from JSON file
with open("Formicarium.json", "r") as file:
    contract_data = json.load(file)

# Extract ABI
abi = contract_data["abi"]

RPC_URL = "https://sepolia.base.org"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

contract_address = os.getenv("FORMICARIUM_TEST_ADDRESS")
printer_address = os.getenv("ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
contract = web3.eth.contract(address=contract_address, abi=abi)

# Function to sign an order
def sign_order(order_id):
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
def execute_new_order():
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
def complete_order_provider(order_id):
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
def transfer_funds_provider(order_id):
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

# Event Handler
async def handle_event(event):
    if event['event'] == "OrderCreated":
        if event['args']['printerId'] == printer_address:
            print(f"Arguments: {event['args']}")
            # SPROŽIMO POSTOPEK PODPISA NAROČILA
            # - Prvo pogledamo ali parametri naročila ustrezajo (enako kot pri API klicu)
            # - Podpišemo na SC

    if event['event'] == "OrderCompleted":
        if event['args']['printerId'] == printer_address:
            print(f"Arguments: {event['args']}")
            # SPROŽIMO NASLEDNJI ORDER
            # - Kličemo OctoPrint API da preverimo stanje
            # - Kličemo SC za izvedbo naslednjega naročila
    
    elif event['event'] == "OrderStarted":
        if event['args']['printerId'] == printer_address:
            print(f"Arguments: {event['args']}")
            # SPROŽIMO POSTOPEK TISKANJA
            # - Najdemo Gkodo
            # - Pošljemo Gkodo na printer
            # - Poženemo tiskanje


# Async Listener for Multiple Events
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

            for log in new_logs:
                event_data = contract.events.OrderCreated().process_log(log)
                await handle_event(event_data)

            latest_block = web3.eth.get_block('latest')["number"] + 1  # Move to the next block

        except Exception as e:
            print(f"Error fetching events: {e}")

        await asyncio.sleep(1)  # Avoid excessive polling


# Run Listener
async def reconnect():
    while True:
        try:
            await listen_events()
        except Exception as e:
            print(f"WebSocket connection lost: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


asyncio.run(reconnect())
