import pandas as pd
import numpy as np

print("📥 正在读取本地数据...")

# 南向资金
south = pd.read_csv("south_money_daily.csv", usecols=[0, 1, 2, 3, 4] )
south.columns = ["date", "net_buy", "buy_amt", "sell_amt", "cumulative"]
south['date'] = pd.to_datetime(south['date'])
print(south)

# VHSI（恒生波幅指数）
vhsi = pd.read_csv("vhsi_daily.csv")
vhsi.columns = ["date", "open", "high", "low", "latest"]
vhsi['date'] = pd.to_datetime(vhsi['date'])
vhsi = vhsi[['date', 'latest']].rename(columns={'latest': 'vhsi'})

# HSI（恒生指数）
hsi = pd.read_csv("hsi_daily.csv")
hsi.columns = ["date", "open", "high", "low", "latest"]
hsi['date'] = pd.to_datetime(hsi['date'])
hsi = hsi[['date', 'latest']].rename(columns={'latest': 'hsi'})

# AH 溢价指数
ah = pd.read_csv("ah_premium_daily.csv")
ah.columns = ["date", "open", "high", "low", "latest"]
ah['date'] = pd.to_datetime(ah['date'])
ah = ah[['date', 'latest']].rename(columns={'latest': 'ah_premium'})

# ----------------------------
# 2. 合并对齐所有数据（以日期为键）
# ----------------------------
df = hsi
for d in [vhsi, ah]:
    df = pd.merge(df, d, on='date', how='outer')

# 南向资金频率较低（工作日），用 outer merge 并前向填充
df = pd.merge(df, south[['date', 'net_buy']], on='date', how='outer')
df = df.sort_values('date').reset_index(drop=True)

# 填充缺失值（如周末/节假日）
df = df.fillna(method='ffill')

print(f"✅ 数据对齐完成，共 {len(df)} 条记录，时间范围: {df['date'].min().date()} ~ {df['date'].max().date()}")

# ----------------------------
# 3. 特征工程
# ----------------------------

# --- HSI 趋势 ---
df['hsi_ma20'] = df['hsi'].rolling(20).mean()
df['hsi_mom20'] = df['hsi'].pct_change(20)
df['above_ma'] = (df['hsi'] > df['hsi_ma20']).astype(int)

# --- VHSI 分级打分（反向：高波动 = 低分）---
vhsi_80 = df['vhsi'].rolling(252).quantile(0.8)  # 高波动阈值
vhsi_50 = df['vhsi'].rolling(252).quantile(0.5)
vhsi_20 = df['vhsi'].rolling(252).quantile(0.2)  # 低波动

df['vhsi_score'] = np.where(df['vhsi'] >= vhsi_80, 0,
                   np.where(df['vhsi'] >= vhsi_50, 25,
                   np.where(df['vhsi'] >= vhsi_20, 50, 75)))
df['vhsi_score'] = df['vhsi_score'].fillna(50)

# --- 南向资金 ---
# 标准化（滚动 Z-Score）
rolling_mean = df['net_buy'].rolling(252).mean()
rolling_std = df['net_buy'].rolling(252).std()
df['south_z'] = (df['net_buy'] - rolling_mean) / rolling_std
df['south_z'] = df['south_z'].clip(-3, 3)

# 连续流入天数
df['sign'] = np.where(df['net_buy'] > 0, 1, -1)
df['streak'] = 0
current = 0
for i in range(len(df)):
    if df.loc[i, 'sign'] == 1:
        current = current + 1 if current >= 0 else 1
    else:
        current = current - 1 if current <= 0 else -1
    df.loc[i, 'streak'] = current

# 南向综合得分
df['south_base'] = (df['south_z'] + 3) / 6 * 50
df['south_bonus'] = np.clip(np.abs(df['streak']) * 0.5, 0, 25)
df['south_score'] = df['south_base'] + np.where(df['streak'] > 0, df['south_bonus'], -df['south_bonus'])
df['south_score'] = df['south_score'].clip(0, 100)

# --- AH 溢价历史百分位（越高越贪婪）---
df['ah_pct'] = df['ah_premium'].rolling(1000).rank(pct=True) * 100
df['ah_score'] = df['ah_pct']

# --- 趋势得分 ---
mom_score = df['hsi_mom20'].rank(pct=True) * 50
ma_score = df['above_ma'] * 50
trend_score = (mom_score.fillna(25) + ma_score) / 2

# ----------------------------
# 4. 合成恐贪指数（0~100）
# ----------------------------
w_ah = 0.25
w_south = 0.30
w_vhsi = 0.30
w_trend = 0.15

df['fear_greed'] = (
    w_ah * df['ah_score'] +
    w_south * df['south_score'] +
    w_vhsi * df['vhsi_score'] +
    w_trend * trend_score
).clip(0, 100)

# ----------------------------
# 5. 输出与绘图
# ----------------------------
result = df[['date', 'hsi', 'vhsi', 'net_buy', 'ah_premium', 'fear_greed']].copy()
result.to_csv("hk_fear_greed_index_from_local.csv", index=False, encoding='utf-8-sig')

print(f"\n🎯 最新恐贪指数: {result['fear_greed'].iloc[-1]:.1f}")
print(f"   - AH 溢价: {result['ah_premium'].iloc[-1]:.1f}")
print(f"   - 南向净流入: {result['net_buy'].iloc[-1]:.1f} 亿元")
print(f"   - VHSI: {result['vhsi'].iloc[-1]:.1f}")
print(f"   - HSI: {result['hsi'].iloc[-1]:.0f}")

