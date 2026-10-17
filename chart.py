import datetime
import logging
import os
from collections import deque
from datetime import timedelta, timezone,datetime

import matplotlib

from config import DISPLAY_CHARTS

if not DISPLAY_CHARTS:
    matplotlib.use("Agg")  # no GUI needed, safe on servers

from matplotlib import pyplot as plt


def plot_last_minutes(
    history: deque,
    minutes: int = 30,
    filename: str | None = None,
    show_for_seconds: int = 60,
):
    """
    Plot and optionally save (returns the saved file path, or None) the last `minutes` of BTC price history.

    Args:
        history (deque): A deque containing (datetime, price) entries.
        minutes (int): Window size in minutes to include in the plot.
        filename (str, optional): If provided, saves the chart as PNG.
        show_for_seconds (int): Duration to display the chart before auto-close.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    data = [(t, p) for t, p in history if t >= cutoff]

    if not data:
        logging.warning(" Not enough data to plot chart.")
        return None

    times, prices = zip(*data)
    plt.figure(figsize=(8, 4))
    plt.plot(times, prices, marker="o", linestyle="-", color="blue")
    plt.title(f"BTC/USD - Last {minutes} minutes")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Price (USD)")
    plt.grid(True)

    charts_dir = "charts"
    os.makedirs(charts_dir, exist_ok=True)

    filepath = None
    if filename:
        filepath = os.path.join(charts_dir, filename)
        plt.savefig(filepath, dpi=150)
        logging.info(f"Chart saved: {filepath}")

    if DISPLAY_CHARTS:
        plt.show(block=False)
        plt.pause(show_for_seconds)
    plt.close()
    return filepath
