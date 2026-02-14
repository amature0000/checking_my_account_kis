from pykis import PyKis, KisAuth, KisBalance
from datetime import datetime
import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

# 실전투자용 PyKis 객체를 생성합니다.
kis1 = PyKis(KisAuth.load("private/secret.json"), keep_token=True)
kis2 = PyKis(KisAuth.load("private/secret2.json"), keep_token=True)

# 주 계좌 객체를 가져옵니다.
account1 = kis1.account()
account2 = kis2.account()

balance1: KisBalance = account1.balance()
balance2: KisBalance = account2.balance()

print(repr(balance1)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
print(repr(balance2)) # repr을 통해 객체의 주요 내용을 확인할 수 있습니다.
# ================================================
# secret1: 해외주식 전용
# secret2: ISA계좌
# 환율 설정
usd_krw = balance1.deposits['USD'].exchange_rate

symbols = []
invested_krw = []
current_krw = []

# 계좌1 주식
for stock in balance1.stocks:
    symbols.append(stock.symbol)
    invested_krw.append((stock.amount - stock.profit) * usd_krw)
    current_krw.append(stock.amount * usd_krw)

# 계좌 1 현금
for curr in ['KRW', 'USD']:
    c_amount = balance1.deposits[curr].amount
    if c_amount > 0:
        c_krw = c_amount * (usd_krw if curr == 'USD' else 1)
        symbols.append(f"계좌1 {curr}")
        invested_krw.append(c_krw)
        current_krw.append(c_krw)

# 계좌2 주식
for stock in balance2.stocks:
    name = getattr(stock, 'name', stock.symbol)
    symbols.append(name)
    invested_krw.append(stock.amount - stock.profit)
    current_krw.append(stock.amount)

# 계좌 2 현금
c2_krw = balance2.deposits['KRW'].amount
if c2_krw > 0:
    symbols.append("계좌2 KRW")
    invested_krw.append(c2_krw)
    current_krw.append(c2_krw)

# 시각화
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 11))
plt.rc('font', family='Malgun Gothic') 

def draw_detailed_pie(ax, data, title, total_label):
    # 금액이 있는 항목만
    indices = [i for i, v in enumerate(data) if v > 0]
    plot_data = [data[i] for i in indices]
    
    # 라벨에 금액 추가
    plot_labels = [f"{symbols[i]}\n{int(data[i]/10000):,}만원" for i in indices]
    
    colors = plt.get_cmap('Pastel1').colors
    wedgeprops = {'width': 0.3, 'edgecolor': 'w', 'linewidth': 1.5}

    ax.pie(
        plot_data, labels=plot_labels, autopct='%1.1f%%', 
        startangle=140, colors=colors, pctdistance=0.82, 
        wedgeprops=wedgeprops, textprops={'fontsize': 11}
    )
    
    # 중앙에 총액 표시
    ax.text(0, 0, f"{total_label}\n{int(sum(data)):,}원", ha='center', va='center', 
            fontweight='bold', fontsize=14)
    ax.set_title(title, fontsize=20, pad=40)

# 차트 그리기
draw_detailed_pie(ax1, invested_krw, "전체 포트폴리오 투자 원금", "총 투자금")
draw_detailed_pie(ax2, current_krw, "전체 포트폴리오 자산 가치", f"총 평가액({(sum(current_krw) - sum(invested_krw))/sum(invested_krw)*100:.2f}%)")



plt.tight_layout()
today = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"portfolio_analysis_{today}.png"
plt.savefig(filename, dpi=300, bbox_inches='tight')