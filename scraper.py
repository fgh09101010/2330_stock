import requests
import pandas as pd
import yfinance as yf
import datetime
import os

def convert_date_format(date_str):
    """
    將民國年轉西元年（例如 114/05/21 -> 2025/05/21）
    """
    if isinstance(date_str, str) and "/" in date_str:
        parts = date_str.split("/")
        if len(parts) == 3 and len(parts[0]) <= 3:  # 民國年
            year = int(parts[0]) + 1911
            return f"{year}-{parts[1]}-{parts[2]}"
    return date_str

def fetch_adr():
    ticker = yf.Ticker("TSM")
    df = ticker.history(period="max")
    df = df[["Close"]].reset_index()
    df.rename(columns={"Close": "ADR_Close", "Date": "Date"}, inplace=True)
    df["Date"] = df["Date"].dt.date
    return df

def fetch_tw_stock():
    today = datetime.date.today().strftime("%Y%m%d")
    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={today}&stockNo=2330"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    raw = r.json()

    df = pd.DataFrame(raw["data"], columns=raw["fields"])
    df = df.rename(columns={"日期": "Date", "收盤價": "TWS_Close"})

    # 日期轉西元格式
    df["Date"] = df["Date"].apply(convert_date_format)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[["Date", "TWS_Close"]].dropna()
    df["TWS_Close"] = df["TWS_Close"].str.replace(",", "").astype(float)
    df["Date"] = df["Date"].dt.date
    return df

def fetch_usd_twd():
    ticker = yf.Ticker("TWD=X")
    df = ticker.history(period="max")
    df = df[["Close"]].reset_index()
    df.rename(columns={"Close": "USD_TWD", "Date": "Date"}, inplace=True)
    df["Date"] = df["Date"].dt.date
    return df

def main():
    print("Fetching ADR...")
    adr_df = fetch_adr()
    print("Fetching 台股...")
    tw_df = fetch_tw_stock()
    print("Fetching 匯率...")
    fx_df = fetch_usd_twd()

    print("Merging...")
    df = pd.merge(adr_df, fx_df, on="Date", how="inner")
    df = pd.merge(df, tw_df, on="Date", how="inner")

    df["Premium"] = ((df["ADR_Close"] * df["USD_TWD"]) / df["TWS_Close"] - 1) * 100
    df = df.sort_values("Date")

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/merged.csv", index=False)
    print("✅ Saved to data/merged.csv")

if __name__ == "__main__":
    main()
