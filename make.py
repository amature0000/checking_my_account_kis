import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from lib.core.kis_auth import KISAuth
from lib.core.kis_stock import KISStock
from lib.core.kis_balance import KISBalance
from lib.visualizer.draw import draw_portfolio

# pd.set_option('display.max_columns', None)
# pd.set_option('display.float_format', '{:.2f}'.format)

EMPTY_BALANCE = {
            'cash_available': 0,
            'withdraw_available': 0,
            'total_cash': 0,
        }

class Core:
    def __init__(self, key_path='./private', max_workers=8):
        self.key_path = key_path
        self.max_workers = max_workers
        self.kis_auths = []

        for filename in os.listdir(key_path):
            if not filename.endswith('.json'):
                continue

            file_path = os.path.join(key_path, filename)
            auth = self._getAuth(file_path)

            if auth: self.kis_auths.append(auth)

        self.bass_exrt = None

    def run(self):
        if not self.kis_auths:
            print('nothing to inspect, exit.')
            return

        self.stock = pd.DataFrame()
        self.balance = EMPTY_BALANCE

        worker_count = min(self.max_workers, len(self.kis_auths))
        results = []

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_to_auth = {
                executor.submit(self._process, auth): auth
                for auth in self.kis_auths
            }

            for future in as_completed(future_to_auth):
                auth = future_to_auth[future]
                try:
                    res = future.result()
                    if res: results.append(res)
                except Exception as e:
                    print(f'- {auth.name} 조회 실패: {e}')

        if not results:
            print('nothing to inspect, exit.')
            return

        # balance 합계
        for result in results:
            self.balance['cash_available'] += result['balance']['cash_available']
            self.balance['withdraw_available'] += result['balance']['withdraw_available']
            self.balance['total_cash'] += result['balance']['total_cash']

        # stock 합계
        all_stocks = [result['stock'] for result in results]
        self.stock = (
            pd.concat(all_stocks, ignore_index=True)
            .groupby('name', as_index=False)
            .sum()
        )

        # bass_exrt 계산
        self.bass_exrt = next(
            (r.get('bass_exrt') for r in results if r.get('bass_exrt') is not None),
            None,
        )

        print(self.stock)
        print(self.balance)

        draw_portfolio(self.stock, self.balance, self.bass_exrt)

    def _process(self, auth: KISAuth):
        stock, bass_exrt = self._getStock(auth)
        balance = self._getBalance(auth, bass_exrt)
        print(f'완료: {auth.name}')

        return {
            'name': auth.name,
            'stock': stock,
            'balance': balance,
            'bass_exrt': bass_exrt,
        }

    def _getAuth(self, path):
        try:
            return KISAuth(path)
        except Exception as e:
            print(f'- {path} 로드 실패: {e}')
            return None

    def _getStock(self, auth: KISAuth):
        stk = KISStock(auth)
        domestic = stk.get_domestic()
        overseas, bass_exrt = stk.get_overseas()

        stock = pd.concat(
            [domestic, overseas],
            ignore_index=True,
        )
        return stock, bass_exrt

    def _getBalance(self, auth: KISAuth, bass_exrt):
        bal = KISBalance(auth)
        domestic = bal.get_domestic_cash()
        if not bass_exrt: return domestic

        overseas = bal.get_overseas_cash()

        return {
            'cash_available': (
                domestic['cash_available']
                + overseas['cash_available'] * bass_exrt
            ),
            'withdraw_available': (
                domestic['withdraw_available']
                + overseas['withdraw_available'] * bass_exrt
            ),
            'total_cash': (
                domestic['total_cash']
                + overseas['total_cash'] * bass_exrt
            ),
        }

if __name__ == '__main__':
    core = Core()
    core.run()
