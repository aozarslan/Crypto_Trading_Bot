import json
import os
import pandas as pd

def load_orders():
    orders_file = '/Users/cornerback30/Desktop/crypto_trading_bot/orders/orders.json'
    if not os.path.exists(orders_file):
        return []
    
    with open(orders_file, 'r') as file:
        orders = json.load(file)
    
    return orders

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

    df.plot(x='datetime', y='balance', title='Bakiyenin Zaman İçinde Değişimi')

if __name__ == "__main__":
    orders = load_orders()
    if orders:
        df = calculate_performance(orders)
        analyze_performance(df)
    else:
        print("Herhangi bir emir bulunamadı.")