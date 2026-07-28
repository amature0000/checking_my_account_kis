import requests
import json

from lib.logger.logger import Logger
from lib.core.kis_auth import KISAuth

@Logger.apply_to_all_methods(Logger.printstack)
class KISBalance:
    def __init__(self, auth: KISAuth):
        self.auth = auth

    def fetch(self, api_url: str, tr_id: str, params: dict, post_flag: bool = False):
        url = f"{self.auth.base_url}{api_url}"
        headers = self.auth.get_headers()
        
        headers.update({
            "tr_id": tr_id
        })

        if post_flag:
            res = requests.post(url, headers=headers, data=json.dumps(params))
        else:
            res = requests.get(url, headers=headers, params=params)

        return res.json()
    
    def get_domestic_cash(self):
        api_url = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
        tr_id = "TTTC8908R"
        
        params = {
            "CANO": self.auth.cano,
            "ACNT_PRDT_CD": self.auth.acnt_prdt_cd,
            "PDNO": "",
            "ORD_UNPR": "",
            "ORD_DVSN": "01",
            "CMA_EVLU_AMT_ICLD_YN": "Y",
            "OVRS_ICLD_YN": "N"
        }
        
        data = self.fetch(api_url, tr_id, params)
        if data.get("rt_cd") == "0":
            res = data.get("output", {})
            return {
                "cash_available": int(res.get("ord_psbl_cash", 0)),
                "withdraw_available": int(res.get("nrcv_buy_amt", 0)),
                "total_cash": int(res.get("dnca_tot_amt", 0))
            }
        return None

    def get_overseas_cash(self, currency: str = "USD"):
        api_url = "/uapi/overseas-stock/v1/trading/foreign-margin"
        tr_id = "TTTC2101R"
        Logger.log(f"통화: {currency}")
        
        params = {
            "CANO": self.auth.cano,
            "ACNT_PRDT_CD": self.auth.acnt_prdt_cd,
        }
        
        data = self.fetch(api_url, tr_id, params)
        
        if data.get("rt_cd") == "0":
            output = data.get("output", [])
            
            # 입력받은 통화(currency)와 일치하는 데이터 찾기
            for item in output:
                if item.get("crcy_cd") == currency.upper():
                    return {
                        "cash_available": float(item.get("frcr_gnrl_ord_psbl_amt", 0)),
                        "withdraw_available": float(item.get("frcr_dncl_amt1", 0)) - float(item.get("ustl_buy_amt")),
                        "total_cash": float(item.get("frcr_dncl_amt1", 0))
                    }
            
        return None