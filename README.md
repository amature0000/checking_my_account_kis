# Working In Progress
현재 정상적으로 기능하지 않을 수 있음

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

# note
- lib/ 코드들은 kis 공식 샘플코드를 참고했습니다. [바로가기](https://github.com/koreainvestment/open-trading-api)
- lib/ 코드들은 공식 라이브러리가 아니며, 개인 라이브러리입니다.
