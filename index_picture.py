import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 设置中文字体（避免中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # Windows 常用 SimHei
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 定义开始时间
start_date = '2017-01-01'

# 读取已生成的恐贪指数文件
df = pd.read_csv("hk_fear_greed_index_from_local.csv")
df['date'] = pd.to_datetime(df['date'])

# 过滤数据，仅保留2017年至今的数据
df = df[df['date'] >= start_date]

# 按日期排序（确保时间顺序）
df = df.sort_values('date').reset_index(drop=True)

# 创建图形和主坐标轴
fig, ax1 = plt.subplots(figsize=(14, 7))

# 主图：HSI 指数（左轴）
color_hsi = '#1f77b4'
ax1.set_xlabel('日期')
ax1.set_ylabel('恒生指数 (HSI)', color=color_hsi)
ax1.plot(df['date'], df['hsi'], color=color_hsi, linewidth=1.2, label='HSI')
ax1.tick_params(axis='y', labelcolor=color_hsi)
ax1.grid(True, linestyle='--', alpha=0.5)

# 副图：恐贪指数（右轴）
ax2 = ax1.twinx()
color_fg = '#d62728'
ax2.set_ylabel('恐惧贪婪指数 (0~100)', color=color_fg)
ax2.plot(df['date'], df['fear_greed'], color=color_fg, linewidth=1.5, label='Fear & Greed')
ax2.tick_params(axis='y', labelcolor=color_fg)

# 设置恐贪指数背景色区域（可选，增强可视化）
ax2.axhspan(0, 20, color='red', alpha=0.1, label='极度恐惧')
ax2.axhspan(20, 40, color='orange', alpha=0.1, label='恐惧')
ax2.axhspan(40, 60, color='gray', alpha=0.1, label='中性')
ax2.axhspan(60, 80, color='lightgreen', alpha=0.1, label='贪婪')
ax2.axhspan(80, 100, color='green', alpha=0.1, label='极度贪婪')

# 格式化 x 轴日期（避免重叠）
ax1.xaxis.set_major_locator(mdates.YearLocator())
ax1.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
fig.autofmt_xdate()

# 标题
plt.title('港股恐惧贪婪指数 vs 恒生指数 (HSI) - 2017 至今', fontsize=16, pad=20)

# 合并图例（来自主副轴）
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# 调整布局
plt.tight_layout()

# 保存图片（可选）
plt.savefig("hk_fear_greed_vs_hsi_2017_to_now.png", dpi=300, bbox_inches='tight')

# 显示图形
plt.show()