import requests

OCTOPRINT_API_URL = "http://localhost:5000/api"
OCTOPRINT_API_KEY = "fBV0WeIfD_oOQs18gKwnOMGY2-nmsU5y_n44EVh8iwY"

def upload_file_to_octoprint(file_path):
    """Uploads file to OctoPrint"""
    url = 'http://192.168.221.144:80/api/files/local'
    headers = {
        'X-Api-Key': OCTOPRINT_API_KEY
    }
    files = {
        'file': open(file_path, 'rb')
    }
    
    response = requests.post(url, headers=headers, files=files)
    files['file'].close()

    if response.status_code != 201:
        raise Exception(f"Error uploading file: {response.text}")
    
    print('Upload successful! Server responded with:', response.text)
    return True

def start_printing(file_name):
    """Starts printing the uploaded file on OctoPrint"""
    data = {
        "command": "select",
        "print": True
    }
    url = 'http://192.168.221.144:80/api/files/local/' + file_name # example:'test.gco'
    headers = {
        'X-Api-Key': OCTOPRINT_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 204:
        raise Exception(f"Error starting print: {response.text}")
    
    print('Print started successfully!')
    return 'Printed successfully!'

# Test
try:
    rsp = upload_file_to_octoprint('test.gco')
    if rsp:
        start_printing()
except FileNotFoundError:
    print("File not found. Please check the file path.")