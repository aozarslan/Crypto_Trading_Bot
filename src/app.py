import os
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO
import json
import pandas as pd
import plotly
import plotly.express as px

# Uygulamanın kök dizinini alın
app_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(app_dir, '..', 'templates'), static_folder=os.path.join(app_dir, '..', 'static'))
socketio = SocketIO(app)

def load_orders():
    orders_file = '/Users/cornerback30/Desktop/crypto_trading_bot/orders/orders.json'
    if not os.path.exists(orders_file):
        return []
    
    with open(orders_file, 'r') as file:
        orders = json.load(file)
    
    return orders

def calculate_performance(orders):
    if not orders:
        return pd.DataFrame(), 0, 0, 0, 0, 0, 0

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
    
    total_trades = len(df)
    winning_trades = df[df['balance'] > df['balance'].shift(1)].count()['balance']
    losing_trades = total_trades - winning_trades
    win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
    total_profit = df['balance'].iloc[-1] - df['balance'].iloc[0]

    return df, balances[-1], total_trades, winning_trades, losing_trades, win_rate, total_profit

@app.route('/')
def index():
    orders = load_orders()
    orders_df, current_balance, total_trades, winning_trades, losing_trades, win_rate, total_profit = calculate_performance(orders)

    # Grafik oluşturma
    graphJSON = None
    if not orders_df.empty:
        fig = px.line(orders_df, x='datetime', y='balance', title='Bakiyenin Zaman İçinde Değişimi')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', orders=orders, current_balance=current_balance, graphJSON=graphJSON,
                           total_trades=total_trades, winning_trades=winning_trades, losing_trades=losing_trades, 
                           win_rate=win_rate, total_profit=total_profit)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/orders')
def api_orders():
    orders = load_orders()
    return jsonify(orders)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('update', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def notify_new_order(order):
    socketio.emit('new_order', order)
    orders = load_orders()
    orders_df, current_balance, total_trades, winning_trades, losing_trades, win_rate, total_profit = calculate_performance(orders)

    graphJSON = None
    if not orders_df.empty:
        fig = px.line(orders_df, x='datetime', y='balance', title='Bakiyenin Zaman İçinde Değişimi')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    socketio.emit('update_balance', {
        'current_balance': current_balance,
        'graphJSON': graphJSON,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'total_profit': total_profit
    })
if __name__ == "__main__":
    socketio.run(app, host='127.0.0.1', port=5000)