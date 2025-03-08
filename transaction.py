import requests
import os
from dotenv import load_dotenv
import time 

load_dotenv()
# Replace with your Etherscan API key
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

WHALE_THRESHOLD = 100
# Exchange wallets (Binance, Coinbase, Kraken, etc.)
EXCHANGE_WALLETS = {
    "Binance": [
        "0x28C6c06298d514Db089934071355E5743bf21d60",
        "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
    ],
    "Coinbase": [
        "0x503828976D22510aad0201ac7EC88293211D23Da",
    ],
    "Kraken": [
        "0x0A869d79a7052C7f1b55a8EbAbb06A34Df02A27b",
    ]
}

def get_latest_block():
    """Fetch the latest Ethereum block number."""
    url = f"https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return int(response["result"], 16)

def calculate_past_block(latest_block, days_ago=7):
    """Estimate the block number from 'days_ago' days back."""
    blocks_per_day = (24 * 3600) // 12  # ~7,200 blocks per day
    return latest_block - (blocks_per_day * days_ago)

def get_recent_transactions(wallet, start_block, end_block):
    """Fetch ETH transactions for a specific wallet within the block range."""
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&startblock={start_block}&endblock={end_block}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    
    response = requests.get(url).json()
    return response["result"] if response["status"] == "1" else []

def analyze_whale_transactions(transactions, exchange, wallet):
    """Analyze whale transactions to count deposits & withdrawals."""
    deposits = 0
    withdrawals = 0
    total_deposit_amount = 0
    total_withdraw_amount = 0

    for tx in transactions:
        eth_amount = int(tx["value"]) / 10**18  # Convert Wei to ETH
        if eth_amount >= WHALE_THRESHOLD:
            if tx["to"].lower() == wallet.lower():  # Deposit (whale sending ETH to exchange)
                deposits += 1
                total_deposit_amount += eth_amount
            elif tx["from"].lower() == wallet.lower():  # Withdrawal (exchange sending ETH out)
                withdrawals += 1
                total_withdraw_amount += eth_amount

    return deposits, withdrawals, total_deposit_amount, total_withdraw_amount

def track_whales():
    latest_block = get_latest_block()
    past_block = calculate_past_block(latest_block, 7)

    total_deposits = 0
    total_withdrawals = 0
    total_deposit_amount = 0
    total_withdraw_amount = 0

    for exchange, wallets in EXCHANGE_WALLETS.items():
        for wallet in wallets:
            transactions = get_recent_transactions(wallet, past_block, latest_block)
            deposits, withdrawals, deposit_amount, withdraw_amount = analyze_whale_transactions(transactions, exchange, wallet)
            
            total_deposits += deposits
            total_withdrawals += withdrawals
            total_deposit_amount += deposit_amount
            total_withdraw_amount += withdraw_amount

    summary = (
        "\n📢 **Whale Transaction Summary (Last 7 Days)**:\n"
        f"🟢 Whale Deposits: {total_deposits} (Total: {total_deposit_amount:.2f} ETH)\n"
        f"🔴 Whale Withdrawals: {total_withdrawals} (Total: {total_withdraw_amount:.2f} ETH)\n"
        f"🚨 Total whale withdrawals in the last 7 days: {total_withdrawals}"
    )
    return summary

def main():
   print(track_whales())

if __name__ == "__main__":
    main()