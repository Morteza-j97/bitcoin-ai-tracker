

# price_fetcher.py
import logging
import requests
from config import URL


def get_btc_price():
    """
    Gets the latest Bitcoin price in USD from the CoinGecko API.
    :return:
    float: Last price as a decimal number.
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        return float(response.json()["bitcoin"]["usd"])
    except requests.RequestException as e:
        logging.error(f" Error in receiving price: {e}")
        return None
    except (KeyError, ValueError) as e:
        logging.error(f" Data processing error: {e}")
        return None
