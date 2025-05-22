import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from jinja2 import Template
import os

DATA_DIR = "data"
TEMPLATE_PATH = "templates/index.html.j2"
OUTPUT_HTML = "docs/index.html"

def render_plot():
    df = pd.read_csv(os.path.join(DATA_DIR, "merged.csv"), parse_dates=["Date"])
    df = df.sort_values("Date")

    # 將資料轉為每月（取每月最後一天資料）
    df_monthly = df.set_index("Date").resample("ME").last().reset_index()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=["TSMC ADR & 台股每月走勢", "ADR 溢價（月）"]
    )

    # 上圖：價格走勢（月）
    fig.add_trace(go.Scatter(
        x=df_monthly["Date"], y=df_monthly["ADR_TWD"],
        mode="lines+markers", name="ADR_TWD",
        line=dict(color="#1f77b4"), marker=dict(size=6)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_monthly["Date"], y=df_monthly["TWS_Close"],
        mode="lines+markers", name="TWS_Close",
        line=dict(color="#ff7f0e"), marker=dict(size=6)
    ), row=1, col=1)

    # 下圖：Premium (%) 用柱狀圖表示（月）
    fig.add_trace(go.Bar(
        x=df_monthly["Date"], y=df_monthly["Premium"],
        name="Premium (%)",
        marker_color="black",
        opacity=0.7
    ), row=2, col=1)

    # 著色區間（用 shape 畫背景色）
    fig.update_layout(shapes=[
        dict(type="rect", xref="x2", yref="y2",
             x0=df_monthly["Date"].min(), x1=df_monthly["Date"].max(), y0=10, y1=100,
             fillcolor="rgba(255,0,0,0.15)", line_width=0),
        dict(type="rect", xref="x2", yref="y2",
             x0=df_monthly["Date"].min(), x1=df_monthly["Date"].max(), y0=-100, y1=0,
             fillcolor="rgba(0,200,0,0.15)", line_width=0),
        dict(type="rect", xref="x2", yref="y2",
             x0=df_monthly["Date"].min(), x1=df_monthly["Date"].max(), y0=0, y1=10,
             fillcolor="rgba(200,200,200,0.1)", line_width=0)
    ])

    fig.update_layout(
        title=dict(
            text="TSMC ADR 溢價與每月股價走勢圖",
            y=0.95,   # 預設是0.9，可以調高到0.95~1.0
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        height=700,
        legend=dict(x=0, y=1.15, orientation="h"),
        xaxis2_title="日期",
        yaxis_title="價格 (TWD)",
        yaxis2_title="溢價 (%)",
        yaxis2=dict(range=[-10, 30]),
        margin=dict(t=100)  # 增加上方邊界，避免標題被擠壓
    )

    # 分開圖例，價格走勢在上圖，溢價柱狀在下圖
    fig.update_layout(legend_groupclick="toggleitem")

    return fig.to_html(
        include_plotlyjs='cdn',
        full_html=False,
        config={
            "responsive": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["sendDataToCloud"]
        }
    )

def main():
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = Template(f.read())
    plot_html = render_plot()
    html = template.render(title="TSMC 溢價追蹤", plot_html=plot_html)
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
