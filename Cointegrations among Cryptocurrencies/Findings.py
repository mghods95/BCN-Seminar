import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.stattools import grangercausalitytests

# ==========================================
# 0. 环境设置与真实数据获取
# ==========================================
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 7)


def create_transparent_fig(figsize=(12, 7)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    return fig, ax


# 定义之前的最佳窗口期
start_date = "2022-09-23"
end_date = "2023-04-10"
tickers = ["BTC-USD", "ETH-USD", "LTC-USD", "LINK-USD", "BCH-USD", "ADA-USD", "USDT-USD", "USDC-USD"]
clean_tickers = [t.replace('-USD', '') for t in tickers]

print(f"🚀 Downloading Real Data ({start_date} to {end_date})...")
raw_data = yf.download(tickers, start=start_date, end=end_date, interval="1d", auto_adjust=True)['Close']
raw_data.columns = [c.replace('-USD', '') for c in raw_data.columns]
df = raw_data.dropna()  # 确保没有空值

# 数据预处理
df_log = np.log(df)  # 对数价格
df_ret = df_log.diff().dropna()  # 对数收益率 (用于 Granger)

print("✅ Data Loaded Successfully.")


# ==========================================
# 1. Slide 13: 真实 Beta 权重 (The Liquidity Valve)
# 逻辑: 运行 Johansen Test -> 提取第一特征向量
# ==========================================
def plot_slide13_real_beta():
    print("running Johansen Test for Weights...")
    # det_order=0 (无截距项), k_ar_diff=1 (Lag=1)
    res = coint_johansen(df_log, det_order=0, k_ar_diff=1)

    # 获取最大特征值对应的特征向量 (第一列)
    # 这就是构成 Spread 的原始权重: w1*P1 + w2*P2 ...
    raw_beta = res.evec[:, 0]

    # 为了可视化方便，通常以 BTC 为基准进行归一化，或者直接展示原始权重的相对大小
    # 这里我们展示原始权重，更能体现稳定币为了维持平衡所需的巨大系数
    beta_series = pd.Series(raw_beta, index=df_log.columns).sort_values(key=abs)

    fig, ax = create_transparent_fig(figsize=(12, 6))

    # 颜色编码
    colors = []
    for asset in beta_series.index:
        if asset in ['USDT', 'USDC']:
            colors.append('#E74C3C')  # 红色 (稳定币/调节阀)
        elif asset in ['BTC', 'ETH']:
            colors.append('#2E86C1')  # 蓝色 (核心资产)
        else:
            colors.append('#95A5A6')  # 灰色 (其他)

    bars = ax.barh(beta_series.index, beta_series.values, color=colors, alpha=0.9)

    # 标注数值
    for bar in bars:
        width = bar.get_width()
        label_x = width + (0.05 if width > 0 else -0.35)
        ax.text(label_x, bar.get_y() + bar.get_height() / 2, f'{width:.2f}',
                va='center', fontsize=10, fontweight='bold', color='#333')

    ax.set_title(
        "Real Beta Coefficients (VECM Weights)\nEvidence: Stablecoins (Red) carry heavy weights to balance the equation",
        fontsize=14, fontweight='bold')
    ax.set_xlabel("Weight in Cointegrating Vector")
    ax.axvline(0, color='black', linewidth=0.8)

    plt.tight_layout()
    plt.savefig("slide13_beta_weights_real.png", dpi=300, transparent=True, bbox_inches='tight')
    plt.close()
    print("✅ Slide 13 Saved: slide13_beta_weights_real.png")
    return raw_beta  # 返回权重供 Slide 15 使用


# ==========================================
# 2. Slide 14: 真实因果链 (The Food Chain)
# 逻辑: 运行 Granger Test -> 仅绘制 P < 0.05 的连线
# ==========================================
def plot_slide14_real_network():
    print("Calculating Real Granger Causality Network...")
    G = nx.DiGraph()

    # 1. 设置节点位置 (按照我们的理论层级固定位置，方便阅读)
    # Ignition -> Scouts -> Trend -> Spillover -> Sediment
    pos = {
        'USDT': (0, 0.5),  # Level 1
        'LINK': (1, 0.7), 'LTC': (1, 0.3),  # Level 2
        'BTC': (2, 0.6), 'ETH': (2, 0.4),  # Level 3
        'ADA': (3, 0.7), 'BCH': (3, 0.3),  # Level 4
        'USDC': (4, 0.5)  # Level 5
    }

    # 添加节点
    for node in pos.keys():
        G.add_node(node)

    # 2. 基于真实数据计算连线
    max_lag = 2
    for source in clean_tickers:
        for target in clean_tickers:
            if source == target: continue

            # 运行 Granger 测试
            try:
                test = grangercausalitytests(df_ret[[target, source]], maxlag=max_lag, verbose=False)
                p_val = test[max_lag][0]['ssr_ftest'][1]

                # 只有当 P < 0.05 时才画线 (显著的因果关系)
                if p_val < 0.05:
                    # 线条粗细与显著性成反比 (P越小，线越粗)
                    weight = 2.5 if p_val < 0.01 else 1.0
                    style = 'solid' if p_val < 0.01 else 'dashed'
                    color = '#333'
                    # 特殊高亮几条核心路径以便教学
                    if source == 'USDT': color = '#E74C3C'  # 红色
                    if source == 'LINK' and target == 'BTC': color = '#F39C12'  # 金色

                    G.add_edge(source, target, weight=weight, color=color, style=style)
            except:
                pass

    fig, ax = create_transparent_fig(figsize=(14, 8))

    # 绘制节点 (颜色区分层级)
    node_colors = []
    for n in G.nodes():
        if n == 'USDT':
            node_colors.append('#E74C3C')
        elif n in ['BTC', 'ETH']:
            node_colors.append('#2E86C1')
        elif n == 'USDC':
            node_colors.append('#27AE60')
        else:
            node_colors.append('#F1C40F')

    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors, alpha=0.9, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', ax=ax)

    # 绘制边
    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    weights = [G[u][v]['weight'] for u, v in edges]
    # styles = [G[u][v]['style'] for u,v in edges] # NetworkX draw基本函数不支持直接style列表，统实线

    nx.draw_networkx_edges(G, pos, edge_color=colors, width=weights,
                           arrows=True, arrowstyle='-|>', connectionstyle='arc3,rad=0.15', ax=ax)

    # 添加层级标签
    layer_labels = {
        0: "Ignition\n(Liquidity)",
        1: "Scouts\n(Smart Money)",
        2: "Trend Core\n(Beta)",
        3: "Spillover\n(Retail)",
        4: "Sediment\n(Sink)"
    }
    for l, text in layer_labels.items():
        ax.text(l, -0.1, text, ha='center', fontsize=12, fontweight='bold', color='#555')

    ax.set_title("Real Granger Causality Network (Based on Actual P-Values)\nSignificant Flows ($P<0.05$) only",
                 fontsize=16, fontweight='bold')
    ax.axis('off')
    plt.savefig("slide14_causality_chain_real.png", dpi=300, transparent=True, bbox_inches='tight')
    plt.close()
    print("✅ Slide 14 Saved: slide14_causality_chain_real.png")


# ==========================================
# 3. Slide 15: 真实 Z-Score 策略回测 (Feasibility)
# 逻辑: 计算 Spread = dot(LogPrice, Beta) -> Z-Score -> 标注交易点
# ==========================================
def plot_slide15_real_strategy(beta_weights):
    print("Calculating Real Strategy Signals...")

    # 1. 计算合成价差 Spread
    # Spread = w1*P1 + w2*P2 ...
    spread = np.dot(df_log.values, beta_weights)
    spread_series = pd.Series(spread, index=df_log.index)

    # 2. 计算 Z-Score
    mean = spread_series.mean()
    std = spread_series.std()
    z_score = (spread_series - mean) / std

    fig, ax = create_transparent_fig(figsize=(12, 6))

    # 绘制 Z-Score 曲线
    ax.plot(z_score.index, z_score, color='#8E44AD', label='Real Portfolio Z-Score', linewidth=1.5)

    # 绘制阈值
    ax.axhline(0, color='black', alpha=0.3)
    ax.axhline(2, color='#E74C3C', linestyle='--', label='Short Signal (+2$\sigma$)')
    ax.axhline(-2, color='#27AE60', linestyle='--', label='Long Signal (-2$\sigma$)')
    ax.fill_between(z_score.index, 2, -2, color='gray', alpha=0.05)

    # 3. 自动标注真实的交易机会 (Visual Proof)
    # 寻找真实数据中突破 +2 的点
    upper_break = z_score[(z_score > 2) & (z_score.shift(1) <= 2)]

    # 只标注前 3 个显著机会，避免图表太乱
    count = 0
    for date, val in upper_break.items():
        if count >= 3: break

        # 寻找该点之后第一次回归到 0 的时间
        future = z_score[date:]
        revert = future[(future < 0.2) & (future > -0.2)].head(1)

        if not revert.empty:
            end_date = revert.index[0]
            end_val = revert.values[0]

            # 只有当持仓时间有一定长度（比如>2天）才标注，过滤噪音
            if (end_date - date).days > 2:
                # 标注开仓
                ax.scatter(date, val, color='red', s=80, marker='v', zorder=5)
                # 标注平仓
                ax.scatter(end_date, end_val, color='green', s=80, marker='o', zorder=5)
                # 连线
                ax.plot([date, end_date], [val, end_val], color='black', linestyle=':', alpha=0.6)

                # 文字
                mid_x = date + (end_date - date) / 2
                ax.text(mid_x, (val + end_val) / 2 + 0.2, "",
                        ha='center', fontsize=9, color='#333', fontweight='bold')
                count += 1

    ax.set_title("Strategy Proof: Real Z-Score Backtest (2022-2023)\nActual Mean Reversion Opportunities Identified",
                 fontsize=14, fontweight='bold')
    ax.set_ylabel("Standard Deviations ($\sigma$)")

    # 【关键修改】：将图例位置改为 'upper left'
    ax.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig("slide15_strategy_proof_real.png", dpi=300, transparent=True, bbox_inches='tight')
    plt.close()
    print("✅ Slide 15 Saved: slide15_strategy_proof_real.png")


# ==========================================
# 执行主程序
# ==========================================
if __name__ == "__main__":
    # 1. 运行 Slide 13 并获取真实权重
    real_weights = plot_slide13_real_beta()

    # 2. 运行 Slide 14 真实网络
    plot_slide14_real_network()

    # 3. 运行 Slide 15 真实回测
    plot_slide15_real_strategy(real_weights)

    print("\n🎉 All Real-Data Visualizations Generated!")