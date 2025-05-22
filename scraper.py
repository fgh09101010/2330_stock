import requests
import pandas as pd
import yfinance as yf
import datetime
import os
from dateutil.relativedelta import relativedelta
import time
def convert_date_format(date_str):
    """將民國年轉西元年（例如 114/05/21 -> 2025/05/21）"""
    if isinstance(date_str, str) and "/" in date_str:
        parts = date_str.split("/")
        if len(parts) == 3 and len(parts[0]) <= 3:
            year = int(parts[0]) + 1911
            return f"{year}-{parts[1]}-{parts[2]}"
    return date_str

def fetch_adr(start_date, end_date):
    ticker = yf.Ticker("TSM")
    df = ticker.history(start=start_date, end=end_date)
    df = df[["Close"]].reset_index()
    df.rename(columns={"Close": "ADR_Close", "Date": "Date"}, inplace=True)
    df["Date"] = df["Date"].dt.date
    return df

def fetch_usd_twd(start_date, end_date):
    ticker = yf.Ticker("TWD=X")
    df = ticker.history(start=start_date, end=end_date)
    df = df[["Close"]].reset_index()
    df.rename(columns={"Close": "USD_TWD", "Date": "Date"}, inplace=True)
    df["Date"] = df["Date"].dt.date
    return df

def fetch_tw_stock(start_date, end_date):
    dfs = []
    current = start_date.replace(day=1)
    while current <= end_date:
        date_str = current.strftime("%Y%m%d")
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo=2330"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.encoding = 'utf-8'
            raw = r.json()
            if "data" not in raw:
                current += relativedelta(months=1)
                continue
            df = pd.DataFrame(raw["data"], columns=raw["fields"])
            df = df.rename(columns={"日期": "Date", "收盤價": "TWS_Close"})
            df["Date"] = df["Date"].apply(convert_date_format)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df[["Date", "TWS_Close"]].dropna()
            df["TWS_Close"] = df["TWS_Close"].str.replace(",", "").astype(float)
            df["Date"] = df["Date"].dt.date
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ Failed to fetch {date_str}: {e}")
        current += relativedelta(months=1)

    if dfs:
        all_df = pd.concat(dfs)
        return all_df.drop_duplicates(subset="Date")
    return pd.DataFrame(columns=["Date", "TWS_Close"])

def main():
    end_date = datetime.date.today()
    start_date = end_date - relativedelta(years=10)

    print("📈 Fetching ADR (10年)...")
    adr_df = fetch_adr(start_date, end_date)
    
    print("📉 Fetching 台股 (10年)...")
    tw_df = fetch_tw_stock(start_date, end_date)
    
    time.sleep(10)
    print("💱 Fetching 匯率 (10年)...")
    fx_df = fetch_usd_twd(start_date, end_date)

    print("🔄 Merging...")
    df = pd.merge(adr_df, fx_df, on="Date", how="inner")
    df = pd.merge(df, tw_df, on="Date", how="inner")

    df["ADR_TWD"] = df["ADR_Close"] * df["USD_TWD"] / 5  # 一張台股等於5股ADR
    df["Premium"] = (df["ADR_TWD"] / df["TWS_Close"] - 1) * 100

    df = df.sort_values("Date")

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/merged.csv", index=False)
    print("✅ Saved to data/merged.csv")

if __name__ == "__main__":
    main()
