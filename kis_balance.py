import pandas as pd
import time
from kis_auth import KISAuth
import requests
import json

class KISBalance:
    def __init__(self, key_path: str):
        self.auth = KISAuth(key_path)

    def get_domestic(self):
        return self._fetch_balance(
            is_overseas=False,
            api_url="/uapi/domestic-stock/v1/trading/inquire-balance",
            tr_id="TTTC8434R",
            params={
                "CANO": self.auth.cano,
                "ACNT_PRDT_CD": self.auth.acnt_prdt_cd,
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "02",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "00"
            }
        )

    def get_overseas(self, exchange: str = "NASD", currency: str = "USD"):
        return self._fetch_balance(
            is_overseas=True,
            api_url="/uapi/overseas-stock/v1/trading/inquire-balance",
            tr_id="TTTS3012R",
            params={
                "CANO": self.auth.cano,
                "ACNT_PRDT_CD": self.auth.acnt_prdt_cd,
                "OVRS_EXCG_CD": exchange,
                "TR_CRCY_CD": currency
            }
        )

    def fetch(self, api_url: str, tr_id: str, params: dict, post_flag: bool = False, tr_cont: str = ""):
        url = f"{self.auth.base_url}{api_url}"
        headers = self.auth.get_headers()
        
        headers.update({
            "tr_id": tr_id,
            "custtype": "P",
            "tr_cont": tr_cont  # 연속조회 여부
        })
        if post_flag:
            res = requests.post(url, headers=headers, data=json.dumps(params))
        else:
            res = requests.get(url, headers=headers, params=params)

        return res.json(), res.headers
    
    def _fetch_balance(self, is_overseas: bool, api_url: str, tr_id: str, params: dict):
        all_stocks = []
        summary = None
        
        tr_cont = ""
        # 해외는 200 / 국내는 100
        fk_key = "CTX_AREA_FK200" if is_overseas else "CTX_AREA_FK100"
        nk_key = "CTX_AREA_NK200" if is_overseas else "CTX_AREA_NK100"
        
        params[fk_key] = ""
        params[nk_key] = ""

        while True:
            # KISAuth.fetch
            data, headers = self.fetch(
                api_url=api_url, 
                tr_id=tr_id, 
                params=params, 
                tr_cont=tr_cont
            )

            if data.get("rt_cd") != "0":
                print(f"Error: {data.get('msg1')}")
                break

            # output1
            stocks = data.get("output1", [])
            if isinstance(stocks, dict): stocks = [stocks]
            all_stocks.extend(stocks)

            # output2
            if summary is None:
                summary = data.get("output2", [])
                if isinstance(summary, dict): summary = [summary]

            # tr_cont 확인
            tr_cont = headers.get("tr_cont", "")
            
            if tr_cont in ["M", "F"]:
                params[fk_key] = data.get(fk_key.lower(), "")
                params[nk_key] = data.get(nk_key.lower(), "")
                tr_cont = "N" # 다음 요청부터는 'N' 전송
                time.sleep(0.2)
            else:
                break

        return pd.DataFrame(all_stocks), pd.DataFrame(summary)

b = KISBalance("./private/미국주식.json")

one, two = b.get_overseas()

print(one)
print()
print(two)