import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# 创建数据目录
DATA_DIR = "hk_fear_greed_data"
os.makedirs(DATA_DIR, exist_ok=True)

def save_to_csv(df:pd.DataFrame, filename:str):
    """保存 DataFrame 到 CSV，带时间戳备份"""
    path = os.path.join(DATA_DIR, filename)
    # 如果文件存在，先备份
    if os.path.exists(path):
        backup_name = f"{filename.replace('.csv', '')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        os.rename(path, os.path.join(DATA_DIR, backup_name))
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print(f"✅ 已保存: {path}")



def main():
    print("开始获取数据...")

    #1、恒生指数日线（HSI）
    try:
        hsi = ak.stock_hk_index_daily_em(symbol="HSI")
        hsi['date'] = pd.to_datetime(hsi['date'])
        hsi = hsi.sort_values('date').reset_index(drop=True)
        save_to_csv(hsi, "hsi_daily.csv")
    except Exception as e:
        print(f"获取恒生指数日线数据失败: {e}")

    #2、恒生波动率指数日线（VHSI）
    try:
        vhsi = ak.stock_hk_index_daily_em(symbol="VHSI")
        vhsi['date'] = pd.to_datetime(vhsi['date'])
        vhsi = vhsi.sort_values('date').reset_index(drop=True)
        save_to_csv(vhsi, "vhsi_daily.csv")
    except Exception as e:
        print(f"获取恒生波动率指数日线数据失败: {e}")
    #3、南向资金历史数据
    try:
        south_money = ak.stock_hsgt_hist_em(symbol="南向资金")
        # 1. 将中文列名 '日期' 转为 datetime
        south_money['日期'] = pd.to_datetime(south_money['日期'])
    
        # 2. 重命名关键列（可选，便于后续处理）
        south_money = south_money.rename(columns={
        '日期': 'date',
        '当日成交净买额': 'net_buy_amount',      # 单位：亿元人民币
        '历史累计净买额': 'cumulative_net_buy',
        '持股市值': 'holding_market_value'     # 注意：早期可能为0或缺失
        })
    
        # 3. 按日期排序
        south_money = south_money.sort_values('date').reset_index(drop=True)
    
        # 4. 保存
        save_to_csv(south_money, "south_money_daily.csv")
    except Exception as e:
        print(f"获取南向资金历史数据失败: {e}") 

    #AH溢价指数日线
    try:
        ah_df = ak.stock_hk_index_daily_em(symbol="HSAHP")
        ah_df['date'] = pd.to_datetime(ah_df['date'])
        ah_df = ah_df.sort_values('date').reset_index(drop=True)
        save_to_csv(ah_df, "ah_premium_daily.csv")
    except Exception as e:
        print(f"获取AH溢价指数日线数据失败: {e}")
    
    # 恒生指数估值
    try:
        hsi_valuation = ak.index_analysis_daily_sw(symbol="HSI")
        hsi_valuation['date'] = pd.to_datetime(hsi_valuation['date'])
        hsi_valuation = hsi_valuation.sort_values('date').reset_index(drop=True)
        save_to_csv(hsi_valuation, "hsi_valuation_daily.csv")
    except Exception as e:
        print(f"获取恒生指数估值数据失败: {e}")

if __name__ == "__main__":
    main()