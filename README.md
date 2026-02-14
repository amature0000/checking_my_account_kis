# exploit python-kis
python-kis 패키지를 활용해 한국투자증권의 내 계좌(들)의 투자금/현재 가치를 원형 그래프로 시각화합니다.

# required directory structure
```
root/
  ├── private/              # API keys
  │     └── 내계좌1.json
  │     └── 내계좌2.json
  ├── make.py               # 메인 실행 스크립트
  └── requirements.txt      
```
.json 파일의 작성 양식은 python-kis를 참고하십시오.

# how to run
1. 요구 패키지 설치
```bash
pip install -r requirements.txt
```
3. main 코드 실행
```
python make.py
```
