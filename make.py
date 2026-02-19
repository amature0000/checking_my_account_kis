from pykis import PyKis, KisAuth
from datetime import datetime
import os
import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False


private_dir = "./private"
json_files = []

for filename in os.listdir(private_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(private_dir, filename)
        json_files.append(file_path)

balance_dict = {}

def try_catch_balance(file_name):
    try: return PyKis(KisAuth.load(file_path), keep_token=True).account().balance()
    except Exception as e:
        print(f"- {file_name} 로드 실패: {e}")
        return try_catch_balance(file_name)

for file_path in json_files:
    file_name = os.path.basename(file_path)
    balance = try_catch_balance(file_name)
    balance_dict[file_name] = balance

    print(f"- {file_name} 로드 완료")
    print(repr(balance))

# ================================================
def extract_assets(balance, symbols_list, invested_list, current_list, symbols_money_list, current_money_list, account_name="계좌"):
    """
    계좌 잔고 객체에서 주식과 현금 데이터를 추출하여 리스트에 추가합니다.
    """
    # 환율 설정(default 1)
    usd_krw = 1
    if 'USD' in balance.deposits:
        usd_krw = balance.deposits['USD'].exchange_rate

    # 주식 데이터 추출
    for stock in balance.stocks:
        
        # 금액 계산
        is_foreign = hasattr(stock, 'market') and stock.market in ['NASDAQ', 'NYSE', 'AMEX']
        multiplier = usd_krw if is_foreign else 1
        # 종목명 가져오기(미국주식의 경우 symbol, 아니면 name)
        name = getattr(stock, 'symbol', stock.name) if is_foreign else stock.name
        display_name = f"{name} ({int(stock.qty)}주)"
        
        symbols_list.append(display_name)
        invested_list.append((stock.amount - stock.profit) * multiplier)
        current_list.append(stock.amount * multiplier)

    # 현금 자본 추출
    for curr, deposit in balance.deposits.items():
        if deposit.amount > 0:
            multiplier = usd_krw if curr == 'USD' else 1
            c_krw = deposit.amount * multiplier
            
            symbols_money_list.append(f"{account_name} {curr}")
            current_money_list.append(c_krw)

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


symbols = []
invested_krw = []
current_krw = []
symbols_money = []
current_money = []

# 계좌 정보 추출
for account_name, bal in balance_dict.items():
    account_name = account_name.split('.')[0]
    extract_assets(bal, symbols, invested_krw, current_krw, symbols_money, current_money, account_name)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 12))
plt.rc('font', family='Malgun Gothic') 

# 차트 그리기
draw_detailed_pie(ax1, invested_krw, "전체 포트폴리오 투자 원금", "총 투자금")
draw_detailed_pie(ax2, current_krw, "전체 포트폴리오 자산 가치", f"총 평가액({(sum(current_krw) - sum(invested_krw))/sum(invested_krw)*100:.2f}%)")

# 현금 정보
cash_details = "\n".join([f"{name}: {int(val):,}원" for name, val in zip(symbols_money, current_money)])
plt.figtext(0.5, 0.05, cash_details, ha='left', fontsize=15,  bbox=dict(facecolor='white', alpha=0.5, edgecolor='gray', boxstyle='round,pad=1'))
plt.tight_layout(rect=[0, 0.1, 1, 1]) 

today = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"portfolio_analysis_{today}.png"
plt.savefig(filename, dpi=300, bbox_inches='tight')