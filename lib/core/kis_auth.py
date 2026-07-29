import os
import json
import copy
import requests
import yaml
from datetime import datetime

class KISAuth:
    def __init__(self, key_path: str):
        """
        key_path: json 파일 경로
        """
        # 설정 로드
        self.name = os.path.basename(key_path)
        base_path = os.path.dirname(os.path.abspath(key_path))
        
        self.cfg = self._load_key(key_path)

        account = self.cfg['account'].split("-")
        self.__cano = account[0]
        self.__acnt_prdt_cd = account[1]

        # 토큰 저장 경로
        self.config_root = os.path.join(base_path, "TOKEN")
        if not os.path.exists(self.config_root):
            os.makedirs(self.config_root)

        self.token_file = os.path.join(self.config_root, f"KIS_TOKEN_{self.__cano}_{datetime.today().strftime('%Y%m%d')}")
        
        # 상태 변수
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.last_auth_time = datetime.now()
        
        # 헤더 초기화
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "charset": "UTF-8",
            "User-Agent": "Mozilla/5.0"
        }

        # 인증 실행 (토큰 발급 및 환경 설정)
        self._authenticate()
    
    @property
    def cano(self):
        return self.__cano
    
    @property
    def acnt_prdt_cd(self):
        return self.__acnt_prdt_cd

    def _load_key(self, path: str) -> dict:
        # Logger.log(f"대상: {self.name}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_token(self, token: str, expired: str):
        # Logger.log(f"토큰 저장, 만료일: {expired}")
        valid_date = datetime.strptime(expired, "%Y-%m-%d %H:%M:%S")
        with open(self.token_file, "w", encoding="utf-8") as f:
            data = {"token": token, "valid-date": valid_date.strftime("%Y-%m-%d %H:%M:%S")}
            yaml.dump(data, f)

    def _read_token(self):
        try:
            if not os.path.exists(self.token_file):
                return None
            
            with open(self.token_file, "r", encoding="UTF-8") as f:
                tkg_tmp = yaml.load(f, Loader=yaml.FullLoader)

            exp_dt = tkg_tmp["valid-date"]
            now_dt = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            if exp_dt > now_dt:
                # Logger.log(f"유효 토큰 확인, 만료일: {exp_dt}")
                return tkg_tmp["token"]
            return None
        except Exception:
            return None

    def _authenticate(self):
        """토큰 조회 및 발급, 헤더 업데이트"""
        ak1, ak2 = "appkey", "secretkey"
        p = {
            "grant_type": "client_credentials",
            "appkey": self.cfg[ak1],
            "appsecret": self.cfg[ak2]
        }

        saved_token = self._read_token()
        if saved_token is None:
            # Logger.log("유효한 인증토큰 없음. 발급 절차 진행")
            url = f"{self.base_url}/oauth2/tokenP"
            res = requests.post(url, data=json.dumps(p), headers=self.headers)
            
            if res.status_code == 200:
                res_data = res.json()
                my_token = res_data["access_token"]
                my_expired = res_data["access_token_token_expired"]
                self._save_token(my_token, my_expired)
            else:
                raise ConnectionError(f"Auth Fail: {res.text}")
        else:
            my_token = saved_token

        # 헤더 업데이트
        self.headers.update({
            "authorization": f"Bearer {my_token}",
            "appkey": self.cfg[ak1],
            "appsecret": self.cfg[ak2]
        })
        self.last_auth_time = datetime.now()

    def get_headers(self):
        """토큰 유효시간을 체크하고 헤더 반환"""
        n2 = datetime.now()
        if (n2 - self.last_auth_time).seconds >= 86400:
            # Logger.log("토큰 유효시간 만료. 헤더 업데이트")
            self._authenticate()
        return copy.deepcopy(self.headers)