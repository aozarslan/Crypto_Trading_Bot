import os
import time
import logging
import sys

# Betiğin mevcut çalışma dizinini sys.path'e ekleyin
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../ai_models')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../src')

from data_loader import fetch_ohlcv
from strategy import generate_signals
from utils import place_order, check_open_positions
from reinforcement_learning import create_env, train_reinforcement_learning_model, load_trained_model, predict_action

# logs dizininin var olup olmadığını kontrol edin, yoksa oluşturun
log_dir = '/Users/cornerback30/Desktop/crypto_trading_bot/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=os.path.join(log_dir, 'bot.log'), level=logging.INFO)

def main():
    symbol = 'BTC/USDT'
    logging.info(f"{time.asctime()}: Model eğitiliyor.")
    model_path = train_reinforcement_learning_model()  # Reinforcement learning modelini eğit
    model = load_trained_model(model_path)

    while True:
        logging.info(f"{time.asctime()}: Verileri çekmeye başlıyor.")
        df = fetch_ohlcv(symbol)
        logging.info(f"{time.asctime()}: Veriler çekildi: \n{df.tail()}")

        logging.info(f"{time.asctime()}: Sinyaller üretiliyor.")
        df = generate_signals(df)
        logging.info(f"{time.asctime()}: Sinyaller üretildi: \n{df[['SMA50', 'SMA200', 'RSI', 'MACD', 'MACDSignal', 'MACDHist', 'signal', 'position', 'buy_signal', 'sell_signal']].tail()}")

        state = df[['open', 'high', 'low', 'close', 'volume']].values[-1]  # Son durumu al
        action = predict_action(model, state)  # Model ile tahmin yap
        logging.info(f"{time.asctime()}: Modelin tahmin ettiği aksiyon: {action}")

        if action == 1:  # Alış sinyali
            logging.info(f"{time.asctime()}: Alış sinyali. Emir veriliyor.")
            place_order(symbol, 'buy', take_profit=1.05, stop_loss=0.95)  # Take profit %5, Stop loss %5
        elif action == -1:  # Satış sinyali
            logging.info(f"{time.asctime()}: Satış sinyali. Emir veriliyor.")
            place_order(symbol, 'sell', take_profit=0.95, stop_loss=1.05)  # Take profit %5, Stop loss %5
        else:
            logging.info(f"{time.asctime()}: Bekle.")

        logging.info(f"{time.asctime()}: Açık pozisyonlar kontrol ediliyor.")
        check_open_positions(symbol)

        logging.info(f"{time.asctime()}: 1 dakika bekliyor.")
        time.sleep(60)  # 1 dakika bekle

if __name__ == "__main__":
    main()