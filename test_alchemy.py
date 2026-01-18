import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("ALCHEMY_API_KEY")
print("Loaded API key:", API_KEY[:6] + "..." if API_KEY else None)

url = f"https://eth-mainnet.g.alchemy.com/v2/{API_KEY}"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_blockNumber",
    "params": []
}

response = requests.post(url, json=payload)
response.raise_for_status()

print("Alchemy response:", response.json())
