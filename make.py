import pandas as pd
import os

from lib.core.kis_auth import KISAuth
from lib.core.kis_stock import KISStock
from lib.core.kis_balance import KISBalance
from lib.logger.logger import Logger
from lib.visualizer.draw import draw_portfolio

# pd.set_option('display.max_columns', None)
# pd.set_option('display.float_format', '{:.2f}'.format)

@Logger.apply_to_all_methods(Logger.printstack)
class Core:
    def __init__(self, key_path = './private'):
        self.key_path = key_path
        self.kis_auths = []

        for filename in os.listdir(key_path):
            if filename.endswith('.json'):
                file_path = os.path.join(key_path, filename)
                auth = self._getAuth(file_path)
                self.kis_auths.append(auth)

        self.bass_exrt = 1500


    def run(self):
        all_stocks = []
        self.stock = []
        self.balance = {
            "cash_available": 0,
            "withdraw_available": 0,
            "total_cash": 0
        }

        for auth in self.kis_auths:
            print(f"\n대상: {auth.name}")
            stk = self._getStock(auth)
            bal = self._getBalance(auth)

            all_stocks.append(stk)
            self.balance["cash_available"] += bal["cash_available"]
            self.balance["withdraw_available"] += bal["withdraw_available"]
            self.balance["total_cash"] += bal["total_cash"]

        self.stock = pd.concat(all_stocks, ignore_index=True).groupby("name", as_index=False).sum()

        print(self.stock)
        print(self.balance)

        draw_portfolio(self.stock, self.balance, self.bass_exrt)

        
    def _getAuth(self, path):
        try:
            return KISAuth(path, self.key_path)
        except Exception as e:
            print(f"- {path} 로드 실패: {e}")

    def _getStock(self, auth):
        stk = KISStock(auth)
        domestic = stk.get_domestic()
        overseas, self.bass_exrt = stk.get_overseas()

        return pd.concat(
            [domestic, overseas],
            ignore_index=True
        )

    def _getBalance(self, auth: KISAuth):
        bal = KISBalance(auth)
        domestic = bal.get_domestic_cash()
        overseas = bal.get_overseas_cash()
        return {
            "cash_available": domestic["cash_available"] + overseas["cash_available"] * self.bass_exrt,
            "withdraw_available": domestic["withdraw_available"] + overseas["withdraw_available"] * self.bass_exrt,
            "total_cash": domestic["total_cash"] + overseas["total_cash"] * self.bass_exrt,
        }

core = Core()
core.run()