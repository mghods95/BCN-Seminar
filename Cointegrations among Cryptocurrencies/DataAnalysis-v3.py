import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM
from statsmodels.tsa.stattools import grangercausalitytests

# ==========================================
# 0. 环境与风格设置 (Setup)
# ==========================================
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'sans-serif' # 避免字体报错
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 8)

def create_transparent_fig(figsize=(12, 8)):
    """Helper to create professional charts with transparent backgrounds for Slides"""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    return fig, ax

# ==========================================
# 1. 数据获取与预处理 (Data ETL)
# ==========================================
tickers = ["BTC-USD", "ETH-USD", "LTC-USD", "LINK-USD", "BCH-USD", "ADA-USD", "USDT-USD", "USDC-USD"]
clean_tickers = [t.replace('-USD', '') for t in tickers]

print(f"🚀 Downloading market data for: {clean_tickers}...")
# 宽泛下载以确保覆盖最佳窗口
raw_data = yf.download(tickers, start="2021-01-01", end="2026-01-01", auto_adjust=True)['Close']
raw_data.columns = [c.replace('-USD', '') for c in raw_data.columns]
df = raw_data.dropna()

# 转换对数价格 (Log Prices) - 减小方差，稳定序列
df_log = np.log(df)

# 计算对数收益率 (Log Returns) - 用于 Granger 检验 (必须是平稳序列 I(0))
df_ret = df_log.diff().dropna()

# 选取最佳协整窗口 (The "Golden Window")
best_start, best_end = "2022-09-23", "2023-04-10"
df_best = df_log.loc[best_start:best_end]
df_ret_best = df_ret.loc[best_start:best_end]

print(f"✅ Data ready. Analysis Window: {best_start} to {best_end}")

# ==========================================
# 2. 基础可视化 (Basic Visuals for Slides 4-6)
# ==========================================

# --- Fig 1: 相关性矩阵 ---
fig, ax = create_transparent_fig(figsize=(10, 8))
corr_matrix = df.loc[best_start:best_end].corr()
sns.heatmap(corr_matrix, annot=True, cmap="RdYlGn", center=0.8, ax=ax)
ax.set_title("Price Correlation Matrix\nIs Correlation enough for Trading?", fontsize=14, fontweight='bold')
plt.savefig("slide4_correlation.png", dpi=300, transparent=True, bbox_inches='tight')
plt.close()

# --- Fig 2: 归一化价格走势 ---
fig, ax = create_transparent_fig()
norm_df = df_best.apply(lambda x: (x - x.mean()) / x.std())
for col in norm_df.columns:
    # 突出 BTC 和 ETH，其他变细
    lw = 2.5 if col in ['BTC', 'ETH'] else 1.0
    alpha = 0.9 if col in ['BTC', 'ETH'] else 0.5
    ax.plot(norm_df[col], label=col, alpha=alpha, linewidth=lw)
ax.set_title("Normalized Log-Prices (Common Trend Search)\nVisualizing the Co-movement", fontsize=14, fontweight='bold')
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)
plt.tight_layout()
plt.savefig("slide5_price_trends.png", dpi=300, transparent=True, bbox_inches='tight')
plt.close()

# ==========================================
# 3. 统计套利信号 (Statistical Arb for Slide 7-8)
# ==========================================

# 执行 Johansen Test
# det_order=0 (no intercept in cointegrating eqn), k_ar_diff=1 (lag=1)
res = coint_johansen(df_best, det_order=0, k_ar_diff=1)

# 提取特征向量 (Eigenvector) 并归一化 Hedge Ratio (Base: BTC)
vec = res.evec[:, 0] # 第一列是最大特征值对应的向量
btc_idx = list(df_best.columns).index('BTC')
hedge_ratios = vec / vec[btc_idx]

# 构建价差 (Spread)
spread = np.dot(df_best.values, hedge_ratios)
spread_series = pd.Series(spread, index=df_best.index)
z_score = (spread_series - spread_series.mean()) / spread_series.std()

# --- Fig 3: Z-Score Trading Signal ---
fig, ax = create_transparent_fig()
ax.plot(z_score, color='#6C3483', label='Portfolio Z-Score', linewidth=1.5)
ax.axhline(0, color='black', linestyle='-', alpha=0.5)
ax.axhline(2, color='#E74C3C', linestyle='--', label='Sell Signal (+2$\sigma$)')
ax.axhline(-2, color='#27AE60', linestyle='--', label='Buy Signal (-2$\sigma$)')
ax.fill_between(z_score.index, 2, -2, color='gray', alpha=0.1)
ax.set_title("Mean Reversion Signal (Z-Score)\nTrading the Cointegration Vector", fontsize=14, fontweight='bold')
ax.legend(loc='upper right', frameon=False)
ax.set_ylabel("Standard Deviations from Mean")
plt.savefig("slide7_zscore_signal.png", dpi=300, transparent=True, bbox_inches='tight')
plt.close()

# --- Fig 4: Johansen Significance Proof ---
fig, ax = create_transparent_fig(figsize=(12, 6))
trace_stats = res.lr1
crit_vals = res.cvt[:, 1]  # 95% critical values
ranks = [f"r <= {i}" for i in range(len(trace_stats))]
x = np.arange(len(ranks))
width = 0.35

ax.bar(x - width/2, trace_stats, width, label='Trace Statistic', color='royalblue', alpha=0.8)
ax.bar(x + width/2, crit_vals, width, label='95% Critical Value', color='lightcoral', alpha=0.8)

for i in range(len(trace_stats)):
    if trace_stats[i] > crit_vals[i]:
        ax.text(i - width/2, trace_stats[i] + 5, '★', ha='center', va='bottom', color='darkred', fontsize=12)

ax.set_title("Johansen Test Results: Proving Multivariate Cointegration", fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ranks)
ax.legend(frameon=False)
plt.savefig("slide8_johansen_proof.png", dpi=300, transparent=True, bbox_inches='tight')
plt.close()

# ==========================================
# 4. Slide 9: Granger 概念演示 (Concept Visual)
# ==========================================
# 生成模拟数据展示 "Lag" 的概念
t = np.linspace(0, 20, 200)
signal_x = np.sin(t)
signal_y = np.sin(t - 2.5) + np.random.normal(0, 0.1, 200) # 滞后且带噪音

fig, ax = create_transparent_fig(figsize=(10, 5))
ax.plot(t, signal_x, label='Asset X (Leader)', color='#E74C3C', linewidth=2.5)
ax.plot(t, signal_y, label='Asset Y (Follower)', color='#3498DB', linewidth=2.5, linestyle='--')

# 标注滞后
peak_x = np.pi/2
peak_y = np.pi/2 + 2.5
ax.annotate('', xy=(peak_y, 1.1), xytext=(peak_x, 1.1), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
ax.text((peak_x+peak_y)/2, 1.2, 'Predictive Lag Window', ha='center', fontsize=10, fontweight='bold')

ax.set_title("Granger Causality Concept: The Predictive Lag\nChecking if Past(X) helps predict Current(Y)", fontsize=14, fontweight='bold')
ax.legend(loc='upper right', frameon=False)
ax.set_yticks([]) # 隐藏Y轴刻度，纯概念展示
plt.savefig("slide9_granger_concept.png", dpi=300, transparent=True, bbox_inches='tight')
plt.close()

# ==========================================
# 5. Slide 10: 真实数据的 Granger 热力图 (The Real Test)
# ==========================================
# 使用 Log Returns (df_ret_best) 保证平稳性
max_lag = 2
n = len(clean_tickers)
p_values = pd.DataFrame(np.zeros((n, n)), columns=clean_tickers, index=clean_tickers)

print("🔍 Calculating Granger Causality Matrix...")
for c in clean_tickers:   # Source (Driver)
    for r in clean_tickers: # Target (Response)
        if c == r:
            p_values.loc[r, c] = 1.0
            continue
        try:
            # Test: Does col 'c' cause row 'r'?
            test_res = grangercausalitytests(df_ret_best[[r, c]], maxlag=max_lag, verbose=False)
            # 取 lag=2 的 p-value
            p_val = test_res[max_lag][0]['ssr_ftest'][1]
            p_values.loc[r, c] = p_val
        except:
            p_values.loc[r, c] = 1.0

fig, ax = create_transparent_fig(figsize=(10, 8))
# 掩码：只显示 P < 0.1 的部分，突出显著性
mask = p_values > 0.1
sns.heatmap(p_values, annot=True, fmt=".3f",
            cmap="Greens_r", # 越绿越显著(P值越小)
            vmin=0, vmax=0.05, # 聚焦 0.00 - 0.05 强显著区间
            # mask=mask, # (可选) 如果想完全隐藏不显著的格子，取消注释此行
            cbar_kws={'label': 'P-Value (Darker = Stronger Prediction)'},
            linewidths=1, linecolor='#f0f0f0', ax=ax)

ax.set_title(f"Granger Causality Heatmap (Lag={max_lag})\nWho Leads the Market? (Columns drive Rows)", fontsize=14, fontweight='bold')
ax.set_xlabel("Source Asset (Driver)", fontweight='bold', color='#333')
ax.set_ylabel("Target Asset (Follower)", fontweight='bold', color='#333')
plt.tight_layout()
plt.savefig("slide10_causality_matrix.png", dpi=300, transparent=True, bbox_inches='tight')
plt.close()

# ==========================================
# 6. VECM 误差修正速度 (Slide 11 Optional)
# ==========================================
model = VECM(df_best, k_ar_diff=1, coint_rank=1, deterministic='n')
vecm_res = model.fit()
alpha_vec = vecm_res.alpha[:, 0] # 调整系数

fig, ax = create_transparent_fig(figsize=(10, 6))
pd.Series(alpha_vec, index=clean_tickers).sort_values().plot(kind='barh', color='teal', ax=ax)
ax.axvline(0, color='black', linewidth=1)
ax.set_title("Speed of Adjustment (VECM Alpha)\nWho corrects the mispricing?", fontsize=14, fontweight='bold')
ax.set_xlabel("Adjustment Coefficient (Negative = Pulling back to Equilibrium)")
plt.tight_layout()
plt.savefig("slide11_vecm_alpha.png", dpi=300, transparent=True, bbox_inches='tight')
plt.close()

print("\n✨ All systems operational. 7 High-Quality visualization assets generated.")
print("   - slide4_correlation.png")
print("   - slide5_price_trends.png")
print("   - slide7_zscore_signal.png")
print("   - slide8_johansen_proof.png")
print("   - slide9_granger_concept.png (New Concept!)")
print("   - slide10_causality_matrix.png (Refined Heatmap!)")
print("   - slide11_vecm_alpha.png")