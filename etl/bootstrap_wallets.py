import json
import csv
import os
import random
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "data_samples")

TX_FILE = os.path.join(DATA_DIR, "transactions_flat.json")
WALLET_FILE = os.path.join(DATA_DIR, "wallets.csv")

TARGET_WALLETS = 500
MAX_PER_SEED = 40   # number of neighbors per seed wallet

def load_existing_wallets():
    wallets = set()
    with open(WALLET_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            wallets.add(row["wallet_address"].lower())
    return wallets

def load_transactions():
    with open(TX_FILE) as f:
        return json.load(f)

def find_counterparties(transactions, existing_wallets):
    neighbors = defaultdict(set)

    for tx in transactions:
        frm = tx.get("from_address")
        to = tx.get("to_address")

        if not frm or not to:
            continue

        frm = frm.lower()
        to = to.lower()

        if frm in existing_wallets and to not in existing_wallets:
            neighbors[frm].add(to)
        elif to in existing_wallets and frm not in existing_wallets:
            neighbors[to].add(frm)

    return neighbors

def append_wallets(new_wallets):
    with open(WALLET_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for w in new_wallets:
            writer.writerow([w, "organic", "alchemy"])

def main():
    existing = load_existing_wallets()
    txs = load_transactions()
    neighbors = find_counterparties(txs, existing)

    discovered = set()

    for seed, addrs in neighbors.items():
        sample = random.sample(list(addrs), min(MAX_PER_SEED, len(addrs)))
        discovered.update(sample)

    discovered -= existing
    discovered = list(discovered)

    needed = TARGET_WALLETS - len(existing)
    final = discovered[:needed]

    append_wallets(final)

    print(f"Added {len(final)} wallets")
    print(f"Total wallets now ≈ {len(existing) + len(final)}")

if __name__ == "__main__":
    main()
