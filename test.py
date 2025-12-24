import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def save_to_csv(df, filename):
    if not os.path.exists("output"):
        os.makedirs("output")
    df.to_csv(f"output/{filename}", index=False)

hsi_valuation = ak.stock_zh_index_value_csindex(symbol="H30374")  # 恒生指数估值
print(hsi_valuation)

