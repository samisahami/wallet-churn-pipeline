import pandas as pd
import json
import os
from datetime import datetime, timezone

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "data_samples")

INPUT_FILE = os.path.join(DATA_DIR, "transactions_flat.json")
OUTPUT_JSON = os.path.join(DATA_DIR, "wallet_features.json")

OUTPUT_CSV = r"C:\Users\samis\wallet_churn_dbt\wallet_features.csv"

NOW = datetime.now(timezone.utc)

# -----------------------------
# Helpers
# -----------------------------
def parse_timestamp(ts):
    if ts is None:
        return None

    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)

    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None

    return None


def days_between(d1, d2):
    return (d2 - d1).days


# -----------------------------
# Main feature builder
# -----------------------------
def main():
    with open(INPUT_FILE, "r") as f:
        txs = json.load(f)

    wallets = {}

    for tx in txs:
        wallet = tx.get("wallet_address")
        if not wallet:
            continue

        tx_time = parse_timestamp(tx.get("block_timestamp"))
        if tx_time is None:
            continue

        value = float(tx.get("value", 0) or 0)

        if wallet not in wallets:
            wallets[wallet] = {
                "wallet_address": wallet,
                "tx_count": 0,
                "total_value": 0.0,
                "first_tx": tx_time,
                "last_tx": tx_time
            }

        wallets[wallet]["tx_count"] += 1
        wallets[wallet]["total_value"] += value

        if tx_time < wallets[wallet]["first_tx"]:
            wallets[wallet]["first_tx"] = tx_time

        if tx_time > wallets[wallet]["last_tx"]:
            wallets[wallet]["last_tx"] = tx_time

    # -----------------------------
    # Final feature calculations
    # -----------------------------
    features = []

    for w in wallets.values():
        lifetime_days = max(days_between(w["first_tx"], w["last_tx"]), 1)
        days_since_last_tx = days_between(w["last_tx"], NOW)

        features.append({
            "wallet_address": w["wallet_address"],
            "tx_count": w["tx_count"],
            "total_value": round(w["total_value"], 4),
            "avg_tx_value": round(w["total_value"] / w["tx_count"], 4),
            "wallet_lifetime_days": lifetime_days,
            "days_since_last_tx": days_since_last_tx,
            "tx_per_day": round(w["tx_count"] / lifetime_days, 4),
            "churned": 1 if days_since_last_tx > 90 else 0
        })

    # Write JSON (optional, but nice)
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(features, f, indent=2)

    print(f"Saved {len(features)} wallet feature rows → {OUTPUT_JSON}")

    return features


# -----------------------------
# Script entry point
# -----------------------------
if __name__ == "__main__":
    features = main()

    df_features = pd.DataFrame(features)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df_features.to_csv(OUTPUT_CSV, index=False)

    print(f"Wrote CSV → {OUTPUT_CSV} | rows={len(df_features)}")


