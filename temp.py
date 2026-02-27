from kis_auth import KISAuth

kis = KISAuth("./private/ISA계좌.json")

params = {
    "FID_COND_MRKT_DIV_CODE": "J",
    "FID_INPUT_ISCD": "005930"
}

result = kis.fetch(
    api_url="/uapi/domestic-stock/v1/quotations/inquire-price",
    tr_id="FHKST01010100",
    params=params,
    post_flag=False
)

if result.get("rt_cd") == "0":
    data = result["output"]
    print(f"종목명: 삼성전자")
    print(f"현재가: {data['stck_prpr']}원")
    print(f"전일대비: {data['prdy_vrss']}원 ({data['prdy_ctrt']}%)")
else:
    print(f"호출 실패: {result.get('msg1')}")