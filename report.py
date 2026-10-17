import html
import logging
import os
from datetime import datetime

from config import ALERTS_FILENAME, REPORT_FILENAME, REPORT_MAX_ALERTS, REPORT_MAX_ENTRIES

CHARTS_DIR = "charts"

PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="60">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BTC Reports</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 24px auto; padding: 0 16px; background: #f6f7f9; color: #1d2127; }}
  h1 {{ font-size: 1.3rem; }}
  .card {{ background: #fff; border: 1px solid #dde1e6; border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
  .time {{ color: #6b7280; font-size: .85rem; direction: ltr; text-align: left; }}
  img {{ width: 100%; height: auto; border-radius: 6px; }}
  p {{ white-space: pre-wrap; line-height: 1.8; }}
  .alerts {{ background: #fff4e5; border: 1px solid #f5c37a; border-radius: 10px; padding: 12px 16px; margin-bottom: 16px; direction: ltr; text-align: left; font-size: .9rem; }}
  .alerts h2 {{ font-size: 1rem; margin: 0 0 8px; direction: rtl; text-align: right; }}
  .alerts div {{ padding: 2px 0; }}
  .muted {{ color: #6b7280; }}
</style>
</head>
<body>
<h1>گزارش‌های بیت‌کوین (هر ۶۰ ثانیه خودکار رفرش می‌شود)</h1>
{alerts}
{cards}
</body>
</html>
"""


def save_analysis(chart_path: str, analysis: str) -> str:
    """Save the analysis text next to the chart image (same name, .txt)."""
    txt_path = os.path.splitext(chart_path)[0] + ".txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(analysis)
    return txt_path


def save_alert(message: str) -> None:
    """Append a price alert (one line, with local time) to alerts.log."""
    line = f"{datetime.now().astimezone():%Y-%m-%d %H:%M:%S} | {message}"
    try:
        with open(ALERTS_FILENAME, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as e:
        logging.error(f"Could not write alert: {e}")


def _alerts_html() -> str:
    """The newest alerts as an HTML box (empty string if there are none)."""
    if not os.path.exists(ALERTS_FILENAME):
        return ""
    with open(ALERTS_FILENAME, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:
        return ""
    rows = "".join(f"<div>{html.escape(l)}</div>" for l in reversed(lines[-REPORT_MAX_ALERTS:]))
    return f'<div class="alerts"><h2>آخرین هشدارهای قیمت</h2>{rows}</div>'


def update_report():
    """
    Rebuild report.html from the files in charts/ (newest first).
    It reads from disk, so it keeps working after a restart.
    """
    names = os.listdir(CHARTS_DIR) if os.path.isdir(CHARTS_DIR) else []
    pngs = sorted((f for f in names if f.endswith(".png")), reverse=True)[:REPORT_MAX_ENTRIES]

    cards = []
    for png in pngs:
        txt_path = os.path.join(CHARTS_DIR, os.path.splitext(png)[0] + ".txt")
        if os.path.exists(txt_path):
            with open(txt_path, encoding="utf-8") as f:
                text = html.escape(f.read())
            body = f"<p>{text}</p>"
        else:
            body = '<p class="muted">تحلیلی برای این نمودار ذخیره نشده.</p>'
        cards.append(
            f'<div class="card"><div class="time">{html.escape(png)}</div>'
            f'<img src="{CHARTS_DIR}/{html.escape(png)}" alt="chart">{body}</div>'
        )

    try:
        with open(REPORT_FILENAME, "w", encoding="utf-8") as f:
            f.write(PAGE.format(alerts=_alerts_html(), cards="\n".join(cards) or '<p class="muted">هنوز نموداری ساخته نشده.</p>'))
    except OSError as e:
        logging.error(f"Could not write report: {e}")
