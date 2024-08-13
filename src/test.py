import ccxt

def check_balance():
    exchange = ccxt.kucoin({
        'apiKey': '66aa9db1cba55800010af356',
        'secret': 'f6e07ce0-8514-4056-bd4f-31cc9947bcbc',
        'password': 'Al3030aN',  # Sağladığınız passphrase
        'enableRateLimit': True,
    })
    try:
        balance = exchange.fetch_balance()
        print(balance)
    except ccxt.AuthenticationError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_balance()