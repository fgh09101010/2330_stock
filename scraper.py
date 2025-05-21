import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_tsmc_adr():
    ticker = yf.Ticker("TSM")  # TSMC ADR
    df = ticker.history(period="200d")
    df = df[["Close"]].rename(columns={"Close": "ADR_Close"})
    df.index = pd.to_datetime(df.index.date)
    return df

def fetch_tw_stock():
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo=2330"
    all_data = []
    today = datetime.today()
    for i in range(7):  # 抓過去 7 個月（約 140 天）
        month = (today.month - i) % 12 or 12
        year = today.year if today.month - i > 0 else today.year - 1
        date_str = f"{year}{month:02}01"
        resp = requests.get(url.format(date=date_str))
        data = resp.json()
        for row in data.get("data", []):
            date = row[0].replace("/", "-")
            close = float(row[6].replace(",", ""))
            all_data.append((date, close))
    df = pd.DataFrame(all_data, columns=["Date", "TWS_Close"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()
    return df

def fetch_usdtwd():
    url = "https://tw.rter.info/capi.php"
    res = requests.get(url)
    data = res.json()
    rate = data["USDTWD"]["Exrate"]
    df = pd.DataFrame({"USD_TWD": [rate]}, index=[pd.Timestamp.today().normalize()])
    return df

def main():
    adr_df = fetch_tsmc_adr()
    tw_df = fetch_tw_stock()
    fx_df = fetch_usdtwd()
    df = adr_df.join(tw_df, how="inner")
    df = df.join(fx_df, how="ffill")
    df["ADR_TWD"] = df["ADR_Close"] * df["USD_TWD"]
    df["Premium"] = ((df["ADR_TWD"] / df["TWS_Close"]) - 1) * 100
    df.to_csv(os.path.join(DATA_DIR, "merged.csv"))

if __name__ == "__main__":
    main()
