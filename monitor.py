import time
import logging
from collections import deque
from datetime import datetime, timedelta, timezone

from ai_analyzer import analyze_chart
from chart import plot_last_minutes
from config import PRICE_CHECK_INTERVAL, PRICE_LOOKBACK_MINUTES, ALERT_THRESHOLD_PERCENT, HISTORY_HOURS, AI_ENABLED
from report import save_alert, save_analysis, update_report
from price_fetcher import get_btc_price


class BitcoinMonitor:
    """
    A simple monitor for tracking Bitcoin price,
    sending alerts, and saving small charts.
    """

    def __init__(self):
        """
        Keep recent price history in memory (hours defined in config).
        """
        self.history = deque(maxlen=HISTORY_HOURS * 3600 // PRICE_CHECK_INTERVAL)
        self.last_chart_time = None
        self.next_run = time.time()

    def get_price_x_minutes_ago(self, minutes: int):
        """
        Return the price from roughly minutes ago,
        if we have it in history.
        """
        target_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        for timestamp, price in reversed(self.history):
            if timestamp <= target_time:
                return price
        return None

    def check_price(self):
        """
        Fetch current BTC price, store it,
        compare with past values, and alert if change is big enough.
        Also draw a chart every 30 minutes and analyze it with AI.
        """
        now = datetime.now(timezone.utc)
        price = get_btc_price()
        if price is None:
            logging.warning("Failed to fetch price, skipping.")
            return

        self.history.append((now, price))
        ref_price = self.get_price_x_minutes_ago(PRICE_LOOKBACK_MINUTES)

        if ref_price:
            percent_change = ((price - ref_price) / ref_price) * 100
            logging.info(f"Price: {price:.2f} | {PRICE_LOOKBACK_MINUTES}min change: {percent_change:+.2f}%")

            if abs(percent_change) >= ALERT_THRESHOLD_PERCENT:
                direction = "up" if percent_change > 0 else "down"
                message = (
                    f" Bitcoin price alert \n"
                    f"Current price: {price:,.2f} USD\n"
                    f"{PRICE_LOOKBACK_MINUTES}min change: {percent_change:+.2f}% ({direction})"
                )
                short = " ".join(message.split())
                logging.warning(short)
                save_alert(short)
                update_report()
        else:
            logging.info(f"Not enough history for {PRICE_LOOKBACK_MINUTES} minutes ago.")

        # Save chart every 30 minutes
        if self.history and (now - self.history[0][0]) >= timedelta(minutes=30):
            if self.last_chart_time is None or (now - self.last_chart_time >= timedelta(minutes=30)):
                filename = f"btc_chart_{now:%Y%m%d_%H%M}.png"
                chart_path = plot_last_minutes(self.history, minutes=30, filename=filename, show_for_seconds=5)
                self.last_chart_time = now
                if chart_path:
                    self.analyze_and_save(chart_path)

    def analyze_and_save(self, chart_path: str):
        """
        Ask the AI to analyze the chart, show the result in the terminal,
        save it next to the chart and refresh report.html.
        If the AI fails, the chart is still saved and listed in the report.
        """
        if AI_ENABLED:
            analysis = analyze_chart(chart_path)
            if analysis:
                save_analysis(chart_path, analysis)
                logging.info("AI analysis:\n" + analysis)
        update_report()

    def run(self):
        """
        Keep the monitor running forever.
        """
        while True:
            try:
                self.check_price()
            except Exception as e:
                logging.error(f"Error in monitor loop: {e}")

            self.next_run += PRICE_CHECK_INTERVAL
            time.sleep(max(0, self.next_run - time.time()))
