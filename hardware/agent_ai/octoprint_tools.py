import requests
import asyncio
import json

# === Configuration ===
OCTOPRINT_API_URL = "http://192.168.221.144:80/api"
OCTOPRINT_API_KEY = "fBV0WeIfD_oOQs18gKwnOMGY2-nmsU5y_n44EVh8iwY"
POLL_INTERVAL = 5  # Time interval (seconds) for polling API

# Track previous printer state
previous_state = None


### **📤 Upload File to OctoPrint**
def upload_file_to_octoprint(file_path):
    """Uploads a file to OctoPrint"""
    url = f"{OCTOPRINT_API_URL}/files/local"
    headers = {"X-Api-Key": OCTOPRINT_API_KEY}
    files = {"file": open(file_path, "rb")}

    response = requests.post(url, headers=headers, files=files)
    files["file"].close()

    if response.status_code != 201:
        raise Exception(f"❌ Error uploading file: {response.text}")

    print("✅ Upload successful!")
    return True


### **🖨️ Start Printing**
def start_printing(file_name):
    """Starts printing the uploaded file on OctoPrint"""
    url = f"{OCTOPRINT_API_URL}/files/local/{file_name}"
    headers = {
        "X-Api-Key": OCTOPRINT_API_KEY,
        "Content-Type": "application/json"
    }
    data = {"command": "select", "print": True}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 204:
        raise Exception(f"❌ Error starting print: {response.text}")

    print("🚀 Print started successfully!")


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

                print(f"🖨️ Printer state: {state}")

                # If the printer just started printing
                if state == "printing" and previous_state != "printing":
                    print("🎯 Printing started!")

                # If the printer was printing but is now idle/operational
                elif state == "operational" and previous_state == "printing":
                    print("✅ Print completed!")

                # Store previous state
                previous_state = state

            else:
                print(f"⚠️ OctoPrint API error: {response.text}")

        except Exception as e:
            print(f"❌ Error polling OctoPrint API: {e}")

        await asyncio.sleep(POLL_INTERVAL)  # Wait before polling again


### **🛠️ Test Function**
async def test_octoprint():
    """Uploads and starts a print while monitoring OctoPrint API for state changes."""
    # Start API polling in the background
    polling_task = asyncio.create_task(poll_octoprint_status())

    # Upload file and start printing
    file_path = "test.gco"
    if upload_file_to_octoprint(file_path):
        start_printing(file_path)

    # Keep the polling task running
    await polling_task


# **Run the polling function**
asyncio.run(test_octoprint())
