import matplotlib.pyplot as plt
from datetime import datetime
import os

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

def draw_portfolio(stock, balance, exrt = None):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 12))

    # ==============================================================
    labels = [
        f"{row.name} ({int(row.qty)}주)"
        for row in stock.itertuples()
    ]

    invested = stock["invested"].tolist()
    current = stock["current"].tolist()

    colors = plt.get_cmap("Pastel1").colors

    # ==============================================================
    def draw_pie(ax, values, title, center_title):

        valid = [(l, v) for l, v in zip(labels, values) if v > 0]

        labels2 = [
            f"{label}\n{value/10000:,.2f}만원"
            for label, value in valid
        ]

        values2 = [v for _, v in valid]

        ax.pie(
            values2,
            labels=labels2,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.82,
            colors=colors,
            wedgeprops=dict(
                width=0.30,
                edgecolor="white",
                linewidth=1.5
            ),
            textprops=dict(fontsize=11)
        )

        ax.text(
            0,
            0,
            center_title,
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_title(title, fontsize=20, pad=40)

    # ==============================================================
    total_invested = stock["invested"].sum()
    total_current = stock["current"].sum()

    profit_rate = (
        (total_current - total_invested)
        / total_invested
        * 100
    )

    # ==============================================================
    draw_pie(
        ax1,
        invested,
        "전체 포트폴리오 투자 원금",
        f"총 투자금\n{total_invested:,.0f}원"
    )

    draw_pie(
        ax2,
        current,
        "전체 포트폴리오 자산 가치",
        f"총 평가액({profit_rate:.2f}%)\n{total_current:,.0f}원"
    )

    cash_text = (
        f"환율 : {exrt} : 1 \n"
        f"주문가능 현금 : {balance['cash_available']:,.0f}원 \n"
        f"출금가능 금액 : {balance['withdraw_available']:,.0f}원 \n"
        f"총 예수금 : {balance['total_cash']:,.0f}원 "
    )

    plt.figtext(
        0.5,
        0.04,
        cash_text,
        ha="center",
        fontsize=14,
        bbox=dict(
            facecolor="white",
            edgecolor="gray",
            alpha=0.6,
            boxstyle="round,pad=1"
        )
    )

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    
    today = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"portfolio_analysis_{today}.png"

    
    # 토큰 저장 경로
    save_root = "IMG/"
    if not os.path.exists(save_root):
        os.makedirs(save_root)

    plt.savefig(save_root + filename, dpi=300, bbox_inches='tight')
    plt.show()