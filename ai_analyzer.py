import base64
import logging
import mimetypes
import os

from openai import OpenAI

from config import AI_BASE_URL, AI_MODEL, AI_TIMEOUT_SECONDS

SYSTEM_PROMPT = """
تو یک دستیار تحلیل نمودار قیمت بیت‌کوین هستی.
پاسخ را به فارسی و کوتاه (حداکثر ۱۲۰۰ کاراکتر) ارائه بده.
روند قابل مشاهده، تغییرات مهم و محدودیت‌های تحلیل را توضیح بده.
از ساختن اطلاعاتی که در تصویر وجود ندارند خودداری کن.
پیش‌بینی قیمت نکن و توصیه خرید یا فروش نده.
"""

USER_PROMPT = """
این تصویر نمودار قیمت بیت‌کوین را بررسی کن.
روند فعلی و نکات مهمی که از نمودار قابل مشاهده هستند توضیح بده.
"""


def _image_to_data_url(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        raise ValueError("Unknown image format")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def analyze_chart(image_path: str) -> str | None:
    """
    Send the chart image to the AI model and return the Persian analysis.
    Returns None on any failure, so the caller can still send the chart alone.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY is not set; skipping AI analysis.")
        return None

    try:
        client = OpenAI(api_key=api_key, base_url=AI_BASE_URL, timeout=AI_TIMEOUT_SECONDS)
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {"type": "image_url", "image_url": {"url": _image_to_data_url(image_path)}},
                    ],
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"AI analysis failed: {e}")
        return None
