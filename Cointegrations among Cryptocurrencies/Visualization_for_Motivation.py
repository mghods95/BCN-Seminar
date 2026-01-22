import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.vector_ar.vecm import coint_johansen

# 设置绘图风格
# 注意：whitegrid 会生成灰色网格。如果需要完全纯净的透明，可改为 "ticks"
sns.set_theme(style="whitegrid")
plt.rcParams['axes.unicode_minus'] = False


def generate_motivation_visuals():
    # 1. 资产配置
    basket_tickers = ["BTC", "ETH", "LTC", "LINK", "BCH", "ADA", "USDT", "USDC"]
    download_tickers = [t + "-USD" for t in basket_tickers]

    # 获取数据 (聚焦 2023 年底到 2024 年初的叙事分化期)
    print("Fetching market data...")
    try:
        raw_data = yf.download(download_tickers, start="2023-10-01", end="2024-05-01", auto_adjust=True)['Close']
        raw_data.columns = [c.replace('-USD', '') for c in raw_data.columns]
        df_log = np.log(raw_data.dropna())
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    # ==========================================
    # 可视化 1: 双变量 vs 一揽子货币对比
    # ==========================================
    # 计算双变量价差 (BTC-ETH)
    pair_spread = df_log['BTC'] - df_log['ETH']
    pair_spread_series = pd.Series(pair_spread - pair_spread.iloc[0], index=df_log.index)

    # 计算 8 币种系统价差 (基于 Johansen 协整向量)
    res = coint_johansen(df_log, det_order=0, k_ar_diff=1)
    vec = res.evec[:, 0]
    hedge_ratios = vec / vec[df_log.columns.get_loc('BTC')]
    basket_spread_raw = np.dot(df_log.values, hedge_ratios)
    basket_spread_series = pd.Series(basket_spread_raw - np.mean(basket_spread_raw), index=df_log.index)

    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 左图: 双变量失效
    ax1.plot(pair_spread_series, color='#d62728', lw=2)
    ax1.axhline(0, color='black', ls='--', alpha=0.5)
    ax1.set_title("Pairwise Model Fragility (BTC-ETH)\nStructural Divergence", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Log Deviation")

    # 右图: 一揽子货币稳健性
    ax2.plot(basket_spread_series, color='#2ca02c', lw=2)
    ax2.axhline(0, color='black', ls='--', alpha=0.5)
    ax2.set_title("Multi-Asset Basket Robustness (8 Assets)\nSystemic Equilibrium", fontsize=14, fontweight='bold')
    ax2.set_ylabel("Synthesized Spread Deviation")

    plt.tight_layout()
    # 核心修改：设置 transparent=True，bbox_inches='tight' 去除多余白边
    plt.savefig("motivation_comparison.png", dpi=300, transparent=True, bbox_inches='tight')
    print("Success: Image 1 saved as 'motivation_comparison.png' (Transparent)")

    # ==========================================
    # 可视化 2: 共同随机趋势 (Common Trend)
    # ==========================================
    plt.figure(figsize=(12, 7))
    # Z-score 归一化展示“星系共振”
    norm_df = df_log.apply(lambda x: (x - x.mean()) / x.std())

    for col in norm_df.columns:
        # 高亮核心币种，弱化辅助币种
        is_core = col in ['BTC', 'ETH']
        plt.plot(norm_df[col], label=col, alpha=0.8 if is_core else 0.4, lw=2.5 if is_core else 1.2)

    plt.title("The Co-movement Galaxy: Common Stochastic Trend\nShared Macro Drivers across 8 Assets", fontsize=16,
              fontweight='bold')
    plt.ylabel("Standardized Log Price (Z-score)")

    # 调整图例背景，使其在透明底色上也可读
    legend = plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
    legend.get_frame().set_alpha(0.5)

    plt.tight_layout()
    # 核心修改：设置 transparent=True
    plt.savefig("motivation_common_trend.png", dpi=300, transparent=True, bbox_inches='tight')
    print("Success: Image 2 saved as 'motivation_common_trend.png' (Transparent)")

    plt.show()


if __name__ == "__main__":
    generate_motivation_visuals()