import unittest
from src.utils import place_order

class TestUtils(unittest.TestCase):
    def test_place_order(self):
        # Bu test sadece yapının doğru olup olmadığını kontrol eder, gerçek emir vermek yerine sahte veri kullanmalıdır
        symbol = 'BTC/USDT'
        order_type = 'buy'
        try:
            place_order(symbol, order_type, amount=0.001)
        except Exception as e:
            self.fail(f"place_order raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()