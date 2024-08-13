import ccxt
import pandas as pd
import yaml
import time

def load_config():
    config_path = '/Users/cornerback30/Desktop/crypto_trading_bot/config/config.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_exchange():
    config = load_config()
    exchange = ccxt.kucoin({
        'apiKey': config['api_key'],
        'secret': config['api_secret'],
        'password': config['api_passphrase'],
        'enableRateLimit': True,
        'options': {
            'adjustForTimeDifference': True,  # Zaman farkı sorunlarını çözmek için
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
    })
    return exchange

def fetch_ohlcv(symbol, timeframe='1h', limit=200, retries=10, delay=10):
    exchange = get_exchange()
    for attempt in range(retries):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            print(df.head())  # Veri çekme işleminin doğru çalıştığını kontrol etmek için ekleyin
            return df
        except ccxt.NetworkError as e:
            print(f"Network error: {e}, retrying in {delay} seconds...")
            time.sleep(delay)
        except ccxt.AuthenticationError as e:
            print(f"Authentication error: {e}. Please check your API credentials and IP whitelist.")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
    raise ccxt.NetworkError(f"Failed to fetch OHLCV data for {symbol} after {retries} retries.")

if __name__ == "__main__":
    symbol = 'BTC/USDT'
    df = fetch_ohlcv(symbol)
    print(df.head())