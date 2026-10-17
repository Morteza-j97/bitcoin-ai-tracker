"""
Bitcoin Price Monitoring Project Settings
The API key is read from the environment / .env file (see .env.example).
"""
from dotenv import load_dotenv

load_dotenv()

HISTORY_HOURS = 6

PRICE_CHECK_INTERVAL = 60
PRICE_LOOKBACK_MINUTES = 5
ALERT_THRESHOLD_PERCENT = 3.0

CHART_INTERVAL_MINUTES = 30
CHART_FILENAME = "chart.png"
# Keep False on a server (no screen). True only for local debugging.
DISPLAY_CHARTS = False

# AI analysis (OpenAI-compatible API)
AI_ENABLED = True
AI_BASE_URL = "https://api.gapgpt.app/v1"
AI_MODEL = "gpt-4o-mini"
AI_TIMEOUT_SECONDS = 60

# Local HTML report: newest charts + analyses, open it in a browser
REPORT_FILENAME = "report.html"
REPORT_MAX_ENTRIES = 20

# Price alerts are appended to this file and shown at the top of the report
ALERTS_FILENAME = "alerts.log"
REPORT_MAX_ALERTS = 10

URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
