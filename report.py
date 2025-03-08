import requests
import pandas as pd

def get_crypto_indicators(crypto_id="bitcoin", currency="usd"):
    base_url = "https://api.coingecko.com/api/v3"
    
    # Get market data (price, volume, high, low)
    market_data = requests.get(f"{base_url}/coins/markets", params={
        "vs_currency": currency,
        "ids": crypto_id
    }).json()

    if not market_data:
        return {"error": "Invalid cryptocurrency ID or API issue"}

    data = market_data[0]
    
    # Extract basic indicators
    indicators = {
        "current_price": data["current_price"],
        "market_cap": data["market_cap"],
        "total_volume": data["total_volume"],
        "high_24h": data["high_24h"],
        "low_24h": data["low_24h"],
        "price_change_percentage_24h": data["price_change_percentage_24h"]
    }
    
    # Fetch historical prices and volumes for moving averages, RSI, and MACD calculations
    historical = requests.get(f"{base_url}/coins/{crypto_id}/market_chart", params={
        "vs_currency": currency,
        "days": "365",  # Fetch last 365 days of data for 200-day MA
        "interval": "daily"
    }).json()

    if "prices" not in historical or "total_volumes" not in historical:
        return {"error": "Failed to fetch historical data"}

    # Convert historical data into a Pandas DataFrame
    prices = [x[1] for x in historical["prices"]]
    volumes = [x[1] for x in historical["total_volumes"]]
    df = pd.DataFrame({"Close": prices, "Volume": volumes})

    # Calculate Moving Averages
    df["SMA_50"] = df["Close"].rolling(window=50).mean()  # 50-day MA
    df["SMA_200"] = df["Close"].rolling(window=200).mean()  # 200-day MA
    df["EMA_10"] = df["Close"].ewm(span=10, adjust=False).mean()
    
    # Calculate RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI_14"] = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    
    # Calculate Support and Resistance Levels
    df["Support"] = df["Close"].rolling(window=20).min()  # Example: 20-day low
    df["Resistance"] = df["Close"].rolling(window=20).max()  # Example: 20-day high
    
    # Calculate 30-day average volume
    df["Volume_30d_Avg"] = df["Volume"].rolling(window=30).mean()
    
    # Get latest values
    latest_values = df.iloc[-1]
    indicators.update({
        "SMA_50": latest_values["SMA_50"],
        "SMA_200": latest_values["SMA_200"],
        "EMA_10": latest_values["EMA_10"],
        "RSI_14": latest_values["RSI_14"],
        "MACD": latest_values["MACD"],
        "MACD_Signal": latest_values["MACD_Signal"],
        "Current_Volume": latest_values["Volume"],
        "Volume_30d_Avg": latest_values["Volume_30d_Avg"],
        "Support": latest_values["Support"],
        "Resistance": latest_values["Resistance"]
    })
    
    return indicators

# Example usage:
def main():
    crypto_indicators = get_crypto_indicators("ethereum")
    print(crypto_indicators)

if __name__ == '__main__':
    main()