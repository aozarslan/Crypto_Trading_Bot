import unittest
from src.data_loader import fetch_ohlcv

class TestDataLoader(unittest.TestCase):
    def test_fetch_ohlcv(self):
        symbol = 'BTC/USDT'
        df = fetch_ohlcv(symbol)
        self.assertFalse(df.empty)
        self.assertIn('close', df.columns)

if __name__ == '__main__':
    unittest.main()