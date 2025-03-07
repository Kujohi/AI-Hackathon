import requests
import matplotlib.pyplot as plt
import pandas as pd
import json

from datetime import datetime

def get_crypto_price(crypto_id='bitcoin'):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[crypto_id]['usd']
    else:
        return None

def get_historical_data(crypto_id='bitcoin', days=2, value = 'prices'):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        data = data[value]
        times = [datetime.fromtimestamp(d[0] / 1000) for d in data]
        values = [d[1] for d in data]
        
        # Create a DataFrame
        df = pd.DataFrame({'Time': times, 'Value': values})
        return df
    else:
        return None

def show_user_data(wallet_address):
    with open('user_data.json', 'r') as file:
        data = json.load(file)

    for user in data:
        if user['wallet_address'] == wallet_address:
            return user
    return None


def update_portfolio(wallet_address, crypto_id, buy_amount, buy_price):
    # Load JSON data
    with open('user_data.json', 'r') as file:
        data = json.load(file)

    # Iterate over users to find the correct wallet address
    for user in data:
        if user['wallet_address'] == wallet_address:
            if crypto_id in user['portfolio']:
                user['portfolio'][crypto_id]['buy_price'] = (buy_amount*buy_price + user['portfolio'][crypto_id]['buy_price']*user['portfolio'][crypto_id]['amount'])/(buy_amount+user['portfolio'][crypto_id]['amount'])
                user['portfolio'][crypto_id]['amount'] += buy_amount
            else:
                if buy_amount > 0:
                    user["portfolio"][crypto_id] = {"amount": buy_amount, "buy_price": buy_price}            
        

    # Save back to JSON file
    with open('user_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def set_price_alerts(wallet_address, crypto_id, price_alert):
    # Load JSON data
    with open('user_data.json', 'r') as file:
        data = json.load(file)

    # Iterate over users to find the correct wallet address
    for user in data:
        if user['wallet_address'] == wallet_address:
            user['notification_settings']["price_alerts"][crypto_id] = price_alert
         
        

    # Save back to JSON file
    with open('user_data.json', 'w') as file:
        json.dump(data, file, indent=4)        

def main():
    # crypto_id = 'bitcoin' 
    # price = get_crypto_price(crypto_id)
    # if price:
    #     print(f"The current price of {crypto_id} is ${price}")
    # else:
    #     print("Failed to retrieve the price.")

    # historical_data = get_historical_data(crypto_id, days=1, value = 'prices')
    # historical_data.to_csv('data.csv')

    # print(show_user_data(wallet_address= '0x123456789abcdef'))

    update_portfolio(wallet_address= '0x123456789abcdef', crypto_id= 'BTC', buy_amount = 5, buy_price = 100000)

    # set_price_alerts(wallet_address= '0x123456789abcdef', crypto_id= 'XRP', price_alert= 100000)
    

if __name__ == "__main__":
    main()