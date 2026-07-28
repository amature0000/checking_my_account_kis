import pandas as pd
import time
import requests
import json
import datetime

from lib.logger.logger import Logger
from lib.core.kis_auth import KISAuth

@Logger.apply_to_all_methods(Logger.printstack)
class KISStock:
    def __init__(self, kis_auth: KISAuth):
        self.auth = kis_auth

    # NOTE: 종목명 prdt_name, 보유수량 hldg_qty, 투자원금 pchs_amt, 평가금액 evlu_amt
    def get_domestic(self):
        data = self._fetch_balance(
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
        if data.empty: return None

        result = data[["prdt_name", "hldg_qty", "pchs_amt", "evlu_amt"]].copy()
        result.columns = ['name', 'qty', 'invested', 'current']

        result["qty"] = pd.to_numeric(result["qty"])
        result["invested"] = pd.to_numeric(result["invested"])
        result["current"] = pd.to_numeric(result["current"])
        
        return result

    def get_overseas(self, currency: str = "USD"):
        today = datetime.datetime.now().strftime("%Y%m%d")
        Logger.log(f"통화: {currency}, 기준일: {today}")
        
        data = self._fetch_balance(
            is_overseas=True,
            api_url="/uapi/overseas-stock/v1/trading/inquire-present-balance",
            tr_id="CTRP6010R",
            params={
                "CANO": self.auth.cano,
                "ACNT_PRDT_CD": self.auth.acnt_prdt_cd,
                "WCRC_FRCR_DVSN_CD": "02",
                "NATN_CD": "000",
                "TR_CRCY_CD": currency,
                "INQR_DVSN_CD": "00",
                "BASS_DT": today
            }
        )
        if data.empty: return None, 1

        # NOTE: 이름은 prdt_name인데 길어서 pdno로 바꿈
        result = data[["pdno", "cblc_qty13", "frcr_pchs_amt", "frcr_evlu_amt2"]].copy()
        result.columns = ['name', 'qty', 'invested', 'current']

        result["qty"] = pd.to_numeric(result["qty"])
        result["invested"] = pd.to_numeric(result["invested"])
        result["current"] = pd.to_numeric(result["current"])

        exchange_rate = pd.to_numeric(data['bass_exrt']).iloc[0]
        result['invested'] *= exchange_rate
        result['current'] *= exchange_rate
        
        return result, exchange_rate

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
                Logger.log(f"Error: {data.get('msg1')}")
                break
            # output1
            stocks = data.get("output1", [])
            if isinstance(stocks, dict): stocks = [stocks]
            all_stocks.extend(stocks)

            # tr_cont 확인
            tr_cont = headers.get("tr_cont", "")
            
            if tr_cont in ["M", "F"]:
                params[fk_key] = data.get(fk_key.lower(), "")
                params[nk_key] = data.get(nk_key.lower(), "")
                tr_cont = "N" # 다음 요청부터는 'N' 전송
                time.sleep(0.2)
            else:
                break

        return pd.DataFrame(all_stocks)