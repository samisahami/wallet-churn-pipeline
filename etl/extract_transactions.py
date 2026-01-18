import os
import csv
import json
import time
import requests
from dotenv import load_dotenv

# --------------------------------------------------
# Setup
# --------------------------------------------------

load_dotenv()

ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
BASE_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "data_samples")

WALLETS_FILE = os.path.join(DATA_DIR, "wallets.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "raw_transactions.json")

# --------------------------------------------------
# Load wallets
# --------------------------------------------------

def load_wallets(filepath):
    wallets = []
    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            wallets.append({
                "wallet_address": row["wallet_address"],
                "label": row["label"],
                "source": row["source"]
            })
    return wallets

# --------------------------------------------------
# Fetch transactions
# --------------------------------------------------

def fetch_transactions(wallet_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getAssetTransfers",
        "params": [{
            "fromBlock": "0x0",
            "toBlock": "latest",
            "fromAddress": wallet_address,
            "category": ["external", "internal", "erc20"],
            "withMetadata": True,
            "excludeZeroValue": True,
            "maxCount": "0x3e8"
        }]
    }

    response = requests.post(BASE_URL, json=payload)
    response.raise_for_status()

    result = response.json().get("result", {})
    transfers = result.get("transfers", [])

    for tx in transfers:
        tx["wallet_address"] = wallet_address

    print(f"Fetched {len(transfers)} transfers for {wallet_address}")
    return transfers

# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    wallets = load_wallets(WALLETS_FILE)
    all_transactions = []

    for wallet in wallets:
        txs = fetch_transactions(wallet["wallet_address"])
        all_transactions.extend(txs)
        time.sleep(0.25)  # rate limit safety

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_transactions, f, indent=2)

    print(f"\nSaved {len(all_transactions)} transactions to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
