import talib
import pandas as pd

def calculate_indicators(df):
    df['SMA50'] = talib.SMA(df['close'], timeperiod=50)
    df['SMA200'] = talib.SMA(df['close'], timeperiod=200)
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
    df['MACD'], df['MACDSignal'], df['MACDHist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return df

def generate_signals(df):
    df = calculate_indicators(df)
    df['signal'] = 0
    df.loc[df['SMA50'] > df['SMA200'], 'signal'] = 1
    df.loc[df['SMA50'] < df['SMA200'], 'signal'] = -1
    df['position'] = df['signal'].diff()

    df['buy_signal'] = (df['RSI'] < 30) & (df['signal'] == 1)
    df['sell_signal'] = (df['RSI'] > 70) & (df['signal'] == -1)
    
    return df

if __name__ == "__main__":
    from data_loader import fetch_ohlcv
    symbol = 'BTC/USDT'
    df = fetch_ohlcv(symbol, limit=200)
    df = generate_signals(df)
    print(df[['SMA50', 'SMA200', 'RSI', 'MACD', 'MACDSignal', 'MACDHist', 'signal', 'position', 'buy_signal', 'sell_signal']].tail())