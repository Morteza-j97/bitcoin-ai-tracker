# Bitcoin Price Tracker

A small side project I built to keep an eye on the Bitcoin price without staring at a chart all day.

It checks the BTC/USD price every minute. If the price jumps or drops too fast, it prints a warning in the terminal, saves it in `alerts.log`, and shows it at the top of `report.html`. Every 30 minutes it draws a chart of the last half hour, saves it as an image, and asks an AI model to write a short analysis of it 

The analysis is printed in the terminal, saved as a text file next to the chart, and added to a small `report.html` page that shows the newest charts with their analysis. Open it in a browser and it refreshes itself every minute.

If the AI service is down or the key is wrong, nothing breaks. You still get the chart, just without the analysis.

## How it's put together

I kept it plain Python on purpose. No framework, no database, nothing you need to learn first. Each file does one job:

- `main.py` starts everything
- `monitor.py` is the main loop: grabs the price, keeps recent history, checks for big moves, triggers the chart
- `price_fetcher.py` gets the price from CoinGecko
- `chart.py` draws the chart with matplotlib
- `ai_analyzer.py` sends the chart image to the AI and returns its answer
- `report.py` saves alerts and analyses and rebuilds `report.html`
- `config.py` holds the settings

If this ever needed to grow, the obvious next steps would be FastAPI for an API, Celery for scheduling and Postgres or Redis for storing history. For what it does now, that would be overkill.

## Setting it up

You need Python 3.10 or newer.

```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Then copy `.env.example` to `.env` and put your API key in it:

```env
OPENAI_API_KEY=your_api_key_here
```

The key works with any OpenAI-compatible service. I use gapgpt, so the base URL in `config.py` points there. Change `AI_BASE_URL` and `AI_MODEL` if you use something else. The model has to understand images.

Please don't commit `.env`. It's already in `.gitignore`.

Run it:

```bash
python main.py
```

The first chart shows up after about 30 minutes, once there's enough price history.

## What you get

- `charts/btc_chart_<date>_<time>.png`: the chart
- `charts/btc_chart_<date>_<time>.txt`: the AI analysis for that chart
- `alerts.log`: one line per price alert, with the time
- `report.html`: the latest alerts, plus the newest charts and analyses, on one page

## Settings worth knowing about

Everything is in `config.py`. The ones I actually touch:

- `ALERT_THRESHOLD_PERCENT` and `PRICE_LOOKBACK_MINUTES`: how big a move, over how many minutes, counts as an alert (right now 3% in 5 minutes)
- `AI_ENABLED`: set to `False` if you only want charts and alerts
- `REPORT_MAX_ENTRIES` and `REPORT_MAX_ALERTS`: how many charts and alerts `report.html` shows
- `DISPLAY_CHARTS`: leave it `False` on a server, there's no screen to show it on

## Things to keep in mind

- The price history lives in memory only. If you restart the script, the first chart comes about 30 minutes later.
- Charts and analyses pile up in the `charts/` folder and nothing deletes them, so clean it out once in a while.
- The AI only describes what it sees in the chart. Don't treat it as financial advice, I certainly don't.

---
Built by Morteza Jvaheri
