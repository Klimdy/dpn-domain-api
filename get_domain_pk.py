import asyncio
from pyppeteer import launch
import requests
import csv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

# Function to find script URL
async def find_script_url(main_page_url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(main_page_url)
    script_urls = await page.evaluate(
        '''() => {
            return Array.from(document.querySelectorAll('script'))
                        .map(elem => elem.src);
        }'''
    )
    script_url = next((url for url in script_urls if 'main.' in url), None)
    await browser.close()
    return script_url

# Function to get public key
async def get_public_key(script_url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(script_url)
    content = await page.content()
    start = content.find("-----BEGIN PUBLIC KEY-----")
    end = content.find("-----END PUBLIC KEY-----", start)
    public_key = content[start:end] + "-----END PUBLIC KEY-----"
    public_key = public_key.replace("\\n", "\n")
    await browser.close()
    return public_key

# Function to get device ID
def get_device_id():
    response = requests.get("http://34.34.34.34/api/admin/getDeviceId")
    if response.status_code == 200:
        return response.json()["deviceId"]
    else:
        raise Exception("Error getting device ID")

# Password encryption function
def encrypt_password(public_key_text, password):
    public_key = serialization.load_pem_public_key(
        public_key_text.encode(),
        backend=default_backend()
    )
    encrypted = public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode()

# Function for authorization
def authorize(username, encrypted_password):
    url = "http://34.34.34.34/api/admin/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": encrypted_password}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception(f"Authorisation Error: {response.text}")

# Function to get a list of domains and save to CSV
def fetch_and_save_domains(token, device_id):
    api_url = 'http://34.34.34.34/api/smartRoute/getRoutingWhitelist/domain?pageNo=1&pageSize=1000'
    headers = {'Authorization': token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        domain_list = response.json().get("list", [])
        filename = f'domains_list_{device_id}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['domainName', 'tunnelCode'])
            for item in domain_list:
                writer.writerow([item['domainName'], item['tunnelCode']])
        print(f"CSV file '{filename}' successfully created.")
    else:
        print("Error when requesting a list of domains:", response.text)

# Function for using a key, authorization and getting a list of domains
def use_key_for_device_authorize_and_fetch_domains(device_id, password):
    public_key_text = get_public_key_from_file(device_id)
    encrypted_password = encrypt_password(public_key_text, password)
    token = authorize("admin", encrypted_password)
    print(f"Device authorization token {device_id}: {token}")

    fetch_and_save_domains(token, device_id)

# Function to get public key from file
def get_public_key_from_file(device_id):
    filename = f"public_key_{device_id}.pem"
    with open(filename, 'r') as file:
        return file.read()

# Main function
async def main():
    main_page_url = "http://34.34.34.34"
    script_url = await find_script_url(main_page_url)
    print("Found script URL:", script_url)

    public_key = await get_public_key(script_url)
    print("Public key:", public_key)

    device_id = get_device_id()
    print("Device ID:", device_id)

    # Saving the public key to a file
    filename = f"public_key_{device_id}.pem"
    with open(filename, 'w') as file:
        file.write(public_key)
    print(f"The public key is saved in a file {filename}")

    # Usage example
    password = "admin"  # Replace with your password
    use_key_for_device_authorize_and_fetch_domains(device_id, password)

# Running the main function
asyncio.get_event_loop().run_until_complete(main())
