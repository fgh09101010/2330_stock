import pandas as pd
import plotly.graph_objs as go
from jinja2 import Template
import os

DATA_DIR = "data"
TEMPLATE_PATH = "templates/index.html.j2"
OUTPUT_HTML = "docs/index.html"

def render_plot():
    df = pd.read_csv(os.path.join(DATA_DIR, "merged.csv"), parse_dates=["Date"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["ADR_TWD"], mode="lines", name="ADR_TWD"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["TWS_Close"], mode="lines", name="TWS_Close"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Premium"], mode="lines", name="Premium (%)", yaxis="y2"))

    fig.update_layout(
        title="TSMC ADR 溢價走勢圖",
        xaxis_title="日期",
        yaxis=dict(title="價格 (TWD)"),
        yaxis2=dict(title="溢價 (%)", overlaying="y", side="right", showgrid=False),
        legend=dict(x=0, y=1.1, orientation="h")
    )
    return fig.to_html(include_plotlyjs='cdn', full_html=False)

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
