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
contract = web3.eth.contract(address=contract_address, abi=abi)


# Event Handler
async def handle_event(event):
    if event['event'] == "OrderCreated":
        if event['args']['printerId'] == printer_address:
            print(f"Arguments: {event['args']}")
            # SPROŽIMO POSTOPEK PODPISA NAROČILA
    
    elif event['event'] == "OrderStarted":
        if event['args']['printerId'] == printer_address:
            print(f"Arguments: {event['args']}")
            # SPROŽIMO POSTOPEK TISKANJA


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
