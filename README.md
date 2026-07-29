# description
한국투자증권의 내 계좌(들)의 투자금/현재 가치를 원형 그래프로 시각화합니다.

# required directory structure
```
root/
  ├── private/              # API keys
  │     └── 내계좌1.json
  │     └── 내계좌2.json
  │     ...
  ├── lib/                  # 라이브러리 코드
  ├── make.py               # 메인 실행 스크립트
  └── requirements.txt      # 요구 패키지
```
# required .json structure
- appkey: 발급받은 app key
- secretkey: 발급받은 secret key
- account: 계좌번호

# how to run
1. 요구 패키지 설치
```bash
pip install -r requirements.txt
```
2. main 코드 실행
```
python make.py
```

# how to use library (description)
```
lib/
  ├── core/...              # python-kis api를 활용하는 인터페이스
  ├── logger/logger.py      # deprecated
  └── visualizer/draw.py    # 시각화 데이터 출력
```

### core/kis_auth.py
KISAuth 클래스는 python-kis의 인증토큰을 발급하고, request를 날릴 때 필요한 헤더를 작성하고 관리하는 클래스입니다.<br>
생성 시 요구되는 `key_path` 인자는 대상 계좌의 api 키가 담긴 json 파일의 주소를 의미합니다.<br>
json 파일은 앞서 설명한 대로 다음과 같은 형식을 따라야 합니다:
> `{"id": "...", "appkey": "...", "secretkey": "...", "account": "00000000-00", "virtual": false}`

**NOTE: json 파일은 appkey, secretkey 등 중요한 정보를 평문으로 저장하므로 주의가 필요합니다.**<br><br>
KISAuth 클래스는 생성 시 저장된 인증토큰을 확인하고, 유효한 토큰이 없다면 자동으로 인증토큰을 발급합니다.<br>
이때, 한국투자증권에서 오픈api 접근 토큰이 요구되었다는 알림을 받을 수 있습니다.<br>
발급된 토큰은 `key_path` 경로의 하위 디렉토리 `TOKEN`에 저장됩니다.<br>
**NOTE: TOKEN 파일은 발급된 토큰을 평문으로 저장하므로 주의가 필요합니다.**<br><br>

### core/kis_balance.py 및 core/kis_stock.py
KISBalance 및 KISStock 클래스는 대상 계좌의 현금정보 및 주식정보를 확인하는 인터페이스입니다.<br>
생성 시 요구되는 `auth` 인자는 `KISAuth` 객체를 의미합니다.<br>
각 클래스의 메소드인 `get_domestic`, `get_overseas` 등은 각각 메소드 이름에 맞는 데이터를 반환합니다.<br>
메소드 중 `KISStock.get_overseas` 만 반환 타입이 다르며, 환율 정보를 받기 위해 요청한 데이터와 환율 데이터를 튜플 형태로 반환합니다.<br><br>

# note
- lib/ 코드들은 kis 공식 샘플코드를 참고했습니다. [바로가기](https://github.com/koreainvestment/open-trading-api)
- lib/ 코드들은 공식 라이브러리가 아닙니다.