import requests
import pandas as pd
import os

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

def main():
    df = pd.read_csv("data/merged.csv", parse_dates=["Date"])
    latest = df.iloc[-1]
    text = (
        f"📢 TSMC ADR 溢價追蹤\n"
        f"日期: {latest['Date'].date()}\n"
        f"ADR: {latest['ADR_TWD']:.2f} TWD\n"
        f"TSE: {latest['TWS_Close']:.2f} TWD\n"
        f"溢價: {latest['Premium']:.2f}%\n"
        f"[🔗 前往圖表網站](https://你的帳號.github.io/你的Repo/)"
    )
    requests.post(WEBHOOK_URL, json={"content": text})

if __name__ == "__main__":
    main()
