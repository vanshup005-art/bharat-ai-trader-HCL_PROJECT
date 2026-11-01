"""
Plotly Charting & Visualization Library for Indian AI Trading Platform.
Creates institutional-grade interactive charts with modern fintech dark aesthetics.
"""
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.settings import THEME_COLORS

CHART_THEME = {
    "bg_color": THEME_COLORS["card_bg"],
    "paper_color": THEME_COLORS["background"],
    "grid_color": "#1E2738",
    "text_color": "#F3F4F6",
    "bull_color": "#10B981",  # Emerald Green
    "bear_color": "#EF4444",  # Crimson Red
    "accent_blue": "#38BDF8", # Sky
    "accent_purple": "#A855F7",
    "accent_orange": "#F59E0B",
    "vwap_color": "#EC4899"
}


def plot_candlestick_chart(
    df: pd.DataFrame,
    ticker: str,
    show_ma: bool = True,
    show_bb: bool = True,
    show_rsi: bool = True,
    show_macd: bool = True,
    show_stoch: bool = False,
    show_vwap: bool = False
) -> go.Figure:
    """Create comprehensive multi-panel technical candlestick chart."""
    # Determine subplot rows
    specs = [[{"secondary_y": True}]]
    row_heights = [0.55]
    titles = [f"{ticker} Price & Volume"]

    if show_rsi:
        specs.append([{"secondary_y": False}])
        row_heights.append(0.15)
        titles.append("RSI (14) Momentum")

    if show_macd:
        specs.append([{"secondary_y": False}])
        row_heights.append(0.15)
        titles.append("MACD & Signal Histogram")

    if show_stoch:
        specs.append([{"secondary_y": False}])
        row_heights.append(0.15)
        titles.append("Stochastic Oscillator (%K, %D)")

    # Normalize row heights
    total_h = sum(row_heights)
    normalized_heights = [h / total_h for h in row_heights]
    total_rows = len(specs)

    fig = make_subplots(
        rows=total_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        subplot_titles=titles,
        row_heights=normalized_heights,
        specs=specs
    )

    dates = df["Date"] if "Date" in df.columns else df.index

    # 1. Candlestick
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color=CHART_THEME["bull_color"],
            decreasing_line_color=CHART_THEME["bear_color"],
            increasing_fillcolor=CHART_THEME["bull_color"],
            decreasing_fillcolor=CHART_THEME["bear_color"]
        ),
        row=1, col=1, secondary_y=False
    )

    # Volume Bars on Secondary Y Axis
    if "Volume" in df.columns:
        vol_colors = [CHART_THEME["bull_color"] if c >= o else CHART_THEME["bear_color"]
                      for c, o in zip(df["Close"], df["Open"])]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=df["Volume"],
                name="Volume",
                marker_color=vol_colors,
                opacity=0.22,
                showlegend=False
            ),
            row=1, col=1, secondary_y=True
        )

    # Moving Averages
    if show_ma:
        if "SMA_20" in df.columns:
            fig.add_trace(go.Scatter(x=dates, y=df["SMA_20"], line=dict(color=CHART_THEME["accent_orange"], width=1.5), name="SMA 20"), row=1, col=1, secondary_y=False)
        if "SMA_50" in df.columns:
            fig.add_trace(go.Scatter(x=dates, y=df["SMA_50"], line=dict(color=CHART_THEME["accent_blue"], width=1.8), name="SMA 50"), row=1, col=1, secondary_y=False)
        if "SMA_200" in df.columns:
            fig.add_trace(go.Scatter(x=dates, y=df["SMA_200"], line=dict(color=CHART_THEME["accent_purple"], width=2.2), name="SMA 200"), row=1, col=1, secondary_y=False)

    # VWAP
    if show_vwap and "VWAP" in df.columns:
        fig.add_trace(go.Scatter(x=dates, y=df["VWAP"], line=dict(color=CHART_THEME["vwap_color"], width=1.5, dash="dash"), name="VWAP"), row=1, col=1, secondary_y=False)

    # Bollinger Bands
    if show_bb and "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=dates, y=df["BB_Upper"], line=dict(color="rgba(156, 163, 175, 0.4)", width=1, dash="dot"), name="BB Upper"), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=dates, y=df["BB_Lower"], line=dict(color="rgba(156, 163, 175, 0.4)", width=1, dash="dot"), fill="tonexty", fillcolor="rgba(156, 163, 175, 0.05)", name="BB Lower"), row=1, col=1, secondary_y=False)

    current_row = 2

    # RSI Subplot
    if show_rsi and "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=dates, y=df["RSI"], line=dict(color=CHART_THEME["accent_purple"], width=1.8), name="RSI (14)"), row=current_row, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color=CHART_THEME["bear_color"], opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color=CHART_THEME["bull_color"], opacity=0.5, row=current_row, col=1)
        fig.update_yaxes(range=[0, 100], row=current_row, col=1)
        current_row += 1

    # MACD Subplot
    if show_macd and "MACD" in df.columns:
        fig.add_trace(go.Scatter(x=dates, y=df["MACD"], line=dict(color=CHART_THEME["accent_blue"], width=1.5), name="MACD"), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=dates, y=df["MACD_Signal"], line=dict(color=CHART_THEME["accent_orange"], width=1.5), name="Signal"), row=current_row, col=1)
        colors = [CHART_THEME["bull_color"] if val >= 0 else CHART_THEME["bear_color"] for val in df["MACD_Hist"]]
        fig.add_trace(go.Bar(x=dates, y=df["MACD_Hist"], marker_color=colors, name="Hist"), row=current_row, col=1)
        current_row += 1

    # Stochastic Subplot
    if show_stoch and "Stoch_K" in df.columns:
        fig.add_trace(go.Scatter(x=dates, y=df["Stoch_K"], line=dict(color=CHART_THEME["accent_blue"], width=1.5), name="%K"), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=dates, y=df["Stoch_D"], line=dict(color=CHART_THEME["accent_orange"], width=1.5), name="%D"), row=current_row, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color=CHART_THEME["bear_color"], opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color=CHART_THEME["bull_color"], opacity=0.5, row=current_row, col=1)
        fig.update_yaxes(range=[0, 100], row=current_row, col=1)

    chart_height = 550 + (total_rows - 1) * 160

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CHART_THEME["paper_color"],
        plot_bgcolor=CHART_THEME["bg_color"],
        font=dict(color=CHART_THEME["text_color"], size=11, family="Inter, sans-serif"),
        xaxis_rangeslider_visible=False,
        height=chart_height,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Adjust secondary y-axis volume scale so it doesn't overlap candles
    fig.update_yaxes(showgrid=False, secondary_y=True, row=1, col=1, range=[0, df["Volume"].max() * 4] if "Volume" in df.columns else None)
    return fig


def plot_anomalies_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Plot price chart highlighting institutional surges and statistical anomalies."""
    fig = go.Figure()
    dates = df["Date"] if "Date" in df.columns else df.index

    fig.add_trace(go.Scatter(
        x=dates,
        y=df["Close"],
        mode="lines",
        name=f"{ticker} Close",
        line=dict(color="#38BDF8", width=2)
    ))

    if "Is_Anomaly" in df.columns:
        anomalies = df[df["Is_Anomaly"]]
        if not anomalies.empty:
            anom_dates = anomalies["Date"] if "Date" in anomalies.columns else anomalies.index
            fig.add_trace(go.Scatter(
                x=anom_dates,
                y=anomalies["Close"],
                mode="markers",
                name="Anomaly Detected",
                text=anomalies["Anomaly_Type"],
                marker=dict(
                    color="#F87171",
                    size=10,
                    symbol="diamond",
                    line=dict(color="#FFFFFF", width=1.5)
                ),
                hovertemplate="<b>Date</b>: %{x}<br><b>Price</b>: ₹%{y:,.2f}<br><b>Alert</b>: %{text}<extra></extra>"
            ))

    fig.update_layout(
        template="plotly_dark",
        title=f"🚨 Statistical Anomaly & Institutional Flow Radar: {ticker}",
        paper_bgcolor=CHART_THEME["paper_color"],
        plot_bgcolor=CHART_THEME["bg_color"],
        font=dict(color=CHART_THEME["text_color"]),
        height=450,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def plot_equity_curve(dates: List[str], equity_curve: List[float], benchmark_curve: List[float]) -> go.Figure:
    """Plot backtest equity curve vs benchmark."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=equity_curve,
        name="AI Strategy Equity",
        line=dict(color=CHART_THEME["bull_color"], width=2.5),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.1)"
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=benchmark_curve,
        name="Benchmark (Buy & Hold NIFTY)",
        line=dict(color="#9CA3AF", width=1.8, dash="dot")
    ))

    fig.update_layout(
        template="plotly_dark",
        title="📈 Strategy Performance vs Benchmark Equity (₹ INR)",
        paper_bgcolor=CHART_THEME["paper_color"],
        plot_bgcolor=CHART_THEME["bg_color"],
        font=dict(color=CHART_THEME["text_color"]),
        height=450,
        margin=dict(l=40, r=40, t=50, b=40),
        yaxis=dict(title="Portfolio Capital (₹)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_efficient_frontier(sim_data: Dict[str, Any], max_sharpe: Dict[str, Any], min_vol: Dict[str, Any]) -> go.Figure:
    """Plot Markowitz Efficient Frontier scatter with optimal portfolios."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sim_data["volatilities"],
        y=sim_data["returns"],
        mode="markers",
        name="Simulated Portfolios",
        marker=dict(
            color=sim_data["sharpes"],
            colorscale="Viridis",
            size=5,
            showscale=True,
            colorbar=dict(title="Sharpe Ratio")
        ),
        hovertemplate="Risk (Vol): %{x:.2f}%<br>Expected Return: %{y:.2f}%<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=[max_sharpe["volatility"]],
        y=[max_sharpe["expected_return"]],
        mode="markers+text",
        name="Max Sharpe (Optimal Alpha)",
        text=["⭐️ Max Sharpe"],
        textposition="top center",
        marker=dict(color="#EF4444", size=14, symbol="star")
    ))

    fig.add_trace(go.Scatter(
        x=[min_vol["volatility"]],
        y=[min_vol["expected_return"]],
        mode="markers+text",
        name="Min Volatility (Defensive)",
        text=["💎 Min Volatility"],
        textposition="bottom center",
        marker=dict(color="#38BDF8", size=14, symbol="diamond")
    ))

    fig.update_layout(
        template="plotly_dark",
        title="🎯 Modern Portfolio Theory: Markowitz Efficient Frontier",
        xaxis_title="Expected Annual Volatility (%)",
        yaxis_title="Expected Annual Return (%)",
        paper_bgcolor=CHART_THEME["paper_color"],
        plot_bgcolor=CHART_THEME["bg_color"],
        font=dict(color=CHART_THEME["text_color"]),
        height=500,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def plot_allocation_donut(weights_dict: Dict[str, float], title: str = "Asset Allocation") -> go.Figure:
    """Plot asset allocation donut chart."""
    labels = list(weights_dict.keys())
    values = list(weights_dict.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        textinfo="label+percent",
        marker=dict(colors=["#38BDF8", "#10B981", "#F59E0B", "#EC4899", "#A855F7", "#06B6D4"])
    )])

    fig.update_layout(
        template="plotly_dark",
        title=title,
        paper_bgcolor=CHART_THEME["paper_color"],
        plot_bgcolor=CHART_THEME["bg_color"],
        font=dict(color=CHART_THEME["text_color"]),
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Plot interactive correlation heatmap for multi-stock portfolios."""
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.index,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        text=np.round(corr_df.values, 2),
        texttemplate="%{text}",
        hoverongaps=False
    ))

    fig.update_layout(
        template="plotly_dark",
        title="🔗 Asset Cross-Correlation Matrix",
        paper_bgcolor=CHART_THEME["paper_color"],
        plot_bgcolor=CHART_THEME["bg_color"],
        font=dict(color=CHART_THEME["text_color"]),
        height=400,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig
