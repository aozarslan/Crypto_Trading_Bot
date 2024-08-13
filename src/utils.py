import json
import os
import pandas as pd
import time
import random
from threading import Thread
import matplotlib.pyplot as plt
import sys

# Betiğin mevcut çalışma dizinini sys.path'e ekleyin
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../ai_models')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../src')

from app import notify_new_order  # notify_new_order fonksiyonunu içe aktarın
from data_loader import get_exchange  # Exchange fonksiyonunu içe aktarın
from reinforcement_learning import load_trained_model, predict_action

def load_orders():
    orders_file = '/Users/cornerback30/Desktop/crypto_trading_bot/orders/orders.json'
    if not os.path.exists(orders_file):
        return []
    
    with open(orders_file, 'r') as file:
        orders = json.load(file)
    
    return orders

def save_order(order):
    orders = load_orders()
    orders.append(order)
    
    orders_file = '/Users/cornerback30/Desktop/crypto_trading_bot/orders/orders.json'
    if not os.path.exists(os.path.dirname(orders_file)):
        os.makedirs(os.path.dirname(orders_file))
    
    with open(orders_file, 'w') as file:
        json.dump(orders, file, indent=4)
    
    # Yeni bir emir geldiğinde bildir
    notify_new_order(order)

def generate_random_order():
    symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']
    order_types = ['market', 'limit']
    sides = ['buy', 'sell']
    
    return {
        'id': f'test_order_{int(time.time())}',
        'datetime': pd.Timestamp.now().isoformat(),
        'symbol': random.choice(symbols),
        'type': random.choice(order_types),
        'side': random.choice(sides),
        'price': random.uniform(30000, 50000),
        'amount': random.uniform(0.001, 0.01),
        'cost': random.uniform(30, 500)
    }

def add_random_orders():
    while True:
        order = generate_random_order()
        save_order(order)
        notify_new_order(order)
        time.sleep(60)  # Her 60 saniyede bir yeni emir ekle

def calculate_performance(orders):
    df = pd.DataFrame(orders)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(by='datetime')

    balance = 1000  # Başlangıç bakiyesi (örnek olarak)
    balances = [balance]

    for index, row in df.iterrows():
        if row['side'] == 'buy':
            balance -= row['cost']
        elif row['side'] == 'sell':
            balance += row['cost']
        balances.append(balance)

    df['balance'] = balances[1:]
    return df

def analyze_performance(df):
    total_trades = len(df)
    winning_trades = df[df['balance'] > df['balance'].shift(1)].count()['balance']
    losing_trades = total_trades - winning_trades
    win_rate = winning_trades / total_trades * 100
    total_profit = df['balance'].iloc[-1] - df['balance'].iloc[0]

    print(f"Toplam Ticaret: {total_trades}")
    print(f"Kazanan Ticaretler: {winning_trades}")
    print(f"Kaybeden Ticaretler: {losing_trades}")
    print(f"Başarı Oranı: {win_rate:.2f}%")
    print(f"Toplam Kar/Zarar: {total_profit:.2f}")

    if not os.path.exists('/Users/cornerback30/Desktop/crypto_trading_bot/static'):
        os.makedirs('/Users/cornerback30/Desktop/crypto_trading_bot/static')

    plt.figure()
    df.plot(x='datetime', y='balance', title='Bakiyenin Zaman İçinde Değişimi')
    plt.savefig('/Users/cornerback30/Desktop/crypto_trading_bot/static/balance_chart.png')  # Grafiği dosyaya kaydedin

def place_order(symbol, side, amount=0.001, price=None, take_profit=None, stop_loss=None):
    exchange = get_exchange()
    order = None

    if side == 'buy':
        order = exchange.create_market_buy_order(symbol, amount)
    elif side == 'sell':
        order = exchange.create_market_sell_order(symbol, amount)

    if order:
        order_info = {
            'id': order['id'],
            'datetime': order['datetime'],
            'symbol': symbol,
            'type': order['type'],
            'side': side,
            'price': order['price'] if price is None else price,
            'amount': amount,
            'cost': order['cost'],
            'take_profit': take_profit,
            'stop_loss': stop_loss
        }
        save_order(order_info)
        return order_info
    return None

def check_open_positions(symbol):
    orders = load_orders()
    open_orders = [order for order in orders if order['symbol'] == symbol and 'close_price' not in order]

    exchange = get_exchange()
    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker['last']

    for order in open_orders:
        if order['side'] == 'buy':
            if 'take_profit' in order and current_price >= order['price'] * order['take_profit']:
                close_order(symbol, 'sell', order['amount'], current_price)
            elif 'stop_loss' in order and current_price <= order['price'] * order['stop_loss']:
                close_order(symbol, 'sell', order['amount'], current_price)
        elif order['side'] == 'sell':
            if 'take_profit' in order and current_price <= order['price'] * order['take_profit']:
                close_order(symbol, 'buy', order['amount'], current_price)
            elif 'stop_loss' in order and current_price >= order['price'] * order['stop_loss']:
                close_order(symbol, 'buy', order['amount'], current_price)

def close_order(symbol, side, amount, price):
    exchange = get_exchange()
    if side == 'buy':
        order = exchange.create_market_buy_order(symbol, amount)
    elif side == 'sell':
        order = exchange.create_market_sell_order(symbol, amount)

    if order:
        order_info = {
            'id': order['id'],
            'datetime': order['datetime'],
            'symbol': symbol,
            'type': order['type'],
            'side': side,
            'price': price,
            'amount': amount,
            'cost': order['cost'],
            'close_price': price
        }
        save_order(order_info)
        return order_info
    return None

if __name__ == "__main__":
    orders = load_orders()
    if orders:
        df = calculate_performance(orders)
        analyze_performance(df)
    else:
        print("Herhangi bir emir bulunamadı.")
    
    # Yeni bir thread'de test emirleri oluşturmayı başlat
    Thread(target=add_random_orders).start()