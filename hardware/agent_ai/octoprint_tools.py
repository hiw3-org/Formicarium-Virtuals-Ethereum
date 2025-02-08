import requests
import asyncio
from langchain.tools import tool
import httpx
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hardware.agent_ai.blockchain_tools import complete_order_provider

# === Configuration ===
OCTOPRINT_API_URL = "http://192.168.0.220:80/api"
OCTOPRINT_API_KEY = "fBV0WeIfD_oOQs18gKwnOMGY2-nmsU5y_n44EVh8iwY"
POLL_INTERVAL = 15  # Time interval (seconds) for polling API




output_folder = Path("agents/keychain_design")

# Track previous printer state
previous_state = None


### **📤 Upload File to OctoPrint**
@tool
def upload_file_to_octoprint(file_path):
    """Uploads a file to OctoPrint"""
    url = f"{OCTOPRINT_API_URL}/files/local"
    headers = {"X-Api-Key": OCTOPRINT_API_KEY}
    
    # File to lower case
    file_path = file_path.lower()
    
    # Remove first 2 characters
    file_path = file_path[2:]
    
    
    gcode_path = output_folder / f"{Path(file_path).stem}.gcode"
    gcode_path.parent.mkdir(exist_ok=True)
    
    files = {"file": open(gcode_path, "rb")}

    response = requests.post(url, headers=headers, files=files)
    files["file"].close()

    if response.status_code != 201:
        raise Exception(f"❌ Error uploading file: {response.text}")

    print("✅ Upload successful!")
    return True


### **🖨️ Start Printing**
@tool
def start_printing(file_name):
    """Starts printing the uploaded file on OctoPrint"""
    file_name = file_name.lower()
    
    # Remove first 2 characters
    file_name = file_name[2:]
    
    url = f"{OCTOPRINT_API_URL}/files/local/{file_name}.gcode"
    headers = {
        "X-Api-Key": OCTOPRINT_API_KEY,
        "Content-Type": "application/json"
    }
    data = {"command": "select", "print": True}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 204:
        raise Exception(f"❌ Error starting print: {response.text}")

    print("🚀 Print started successfully!")
    

### **🔄 Optimized Printer Status Retrieval Function**
def get_octoprint_status():
    """Makes a single GET request to OctoPrint API and returns the printer state."""
    try:
        # Request printer state (single GET request)
        response = requests.get(
            f"{OCTOPRINT_API_URL}/printer",
            headers={"X-Api-Key": OCTOPRINT_API_KEY}
        )

        if response.status_code == 200:
            data = response.json()
            return data["state"]["text"].lower()  # Return state as lowercase string, operation or priting

        else:
            print(f"⚠️ OctoPrint API error: {response.text}")
            return None  # Return None in case of an error

    except Exception as e:
        print(f"❌ Error retrieving OctoPrint status: {e}")
        return None  # Return None if an exception occurs



### **🔄 Polling Function to Check Printer Status**
async def poll_octoprint_status():
    """Polls OctoPrint API at intervals to check if the printer is printing."""
    global previous_state

    while True:
        try:
            # Request printer state
            response = requests.get(
                f"{OCTOPRINT_API_URL}/printer",
                headers={"X-Api-Key": OCTOPRINT_API_KEY}
            )

            if response.status_code == 200:
                data = response.json()
                state = data["state"]["text"].lower()
                
                if state == "printing" and previous_state != "printing":
                    print("🎯 Printing started!")

                # If the printer stoped with the print
                if state == "operational" and previous_state == "printing":
                    print("🎯 Printing finished!")
                    prompt = "[Event trigger], Print finished"
                    async with httpx.AsyncClient() as client:
                        response = await client.post("http://localhost:8080/api/create_order_request", json={"prompt": prompt})
                    if response.status_code != 200:
                        print(f"Error processing chat request: {response.text}")
                        return
                    
                elif state == "operational":
                    prompt = "[Event trigger], Printer Operational"
                    async with httpx.AsyncClient() as client:
                        response = await client.post("http://localhost:8080/api/create_order_request", json={"prompt": prompt})
                    if response.status_code != 200:
                        print(f"Error processing chat request: {response.text}")
                        return

                # Store previous state
                previous_state = state

            else:
                print(f"⚠️ OctoPrint API error: {response.text}")

        except Exception as e:
            print(f"❌ Error polling OctoPrint API: {e}")

        await asyncio.sleep(POLL_INTERVAL)  # Wait before polling again


# ### **🛠️ Test Function**
# async def test_octoprint():
#     """Uploads and starts a print while monitoring OctoPrint API for state changes."""
#     # Start API polling in the background
#     polling_task = asyncio.create_task(poll_octoprint_status())

#     # # Upload file and start printing
#     # file_path = "test.gco"
#     # if upload_file_to_octoprint(file_path):
#     #     start_printing(file_path)

#     # Keep the polling task running
#     await polling_task


# # **Run the polling function**
# asyncio.run(test_octoprint())
