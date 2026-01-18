import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "data_samples")

INPUT_FILE = os.path.join(DATA_DIR, "raw_transactions.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "transactions_flat.json")

def normalize(tx):
    return {
        "wallet_address": tx.get("wallet_address"),
        "tx_hash": tx.get("hash"),
        "block_timestamp": tx.get("metadata", {}).get("blockTimestamp"),
        "asset": tx.get("asset"),
        "value": float(tx.get("value") or 0),
        "category": tx.get("category"),
        "from_address": tx.get("from"),
        "to_address": tx.get("to"),
    }

def main():
    with open(INPUT_FILE, "r") as f:
        raw = json.load(f)   # ✅ correct for large JSON array

    normalized = [normalize(tx) for tx in raw]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(normalized, f, indent=2)

    print(f"Flattened {len(normalized)} transactions")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
