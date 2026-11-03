"""Ботты webhook режимінде іске қосатын WSGI қосымшасы (PythonAnywhere тегін хостингі үшін).

Telegram әр жаңа хабарламаны https://<сайт>/webhook адресіне жібереді,
бот оны өңдеп, жауап береді. Сервер тұрақты жұмыс істейді — Mac қажет емес.
"""

import asyncio
import hashlib
import json
import logging

from aiogram.types import Update

import bot as shop

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("beauty_bot.wsgi")

shop.init_db()
shop.apply_settings()
DP = shop.build_dispatcher()
WEBHOOK_PATH = "/webhook"


def webhook_secret() -> str:
    """Telegram-нан келген сұранысты тексеруге арналған құпия (токеннен жасалады)."""
    return hashlib.sha256(("webhook:" + shop.BOT_TOKEN).encode()).hexdigest()[:48]


async def _process(payload: dict) -> None:
    bot = shop.make_bot()
    try:
        update = Update.model_validate(payload, context={"bot": bot})
        await DP.feed_update(bot, update)
    finally:
        await bot.session.close()


def _respond(start_response, status: str, body: str):
    data = body.encode("utf-8")
    start_response(status, [("Content-Type", "text/plain; charset=utf-8"),
                            ("Content-Length", str(len(data)))])
    return [data]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if method == "POST" and path == WEBHOOK_PATH:
        if environ.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN") != webhook_secret():
            return _respond(start_response, "403 Forbidden", "forbidden")
        try:
            size = int(environ.get("CONTENT_LENGTH") or 0)
            payload = json.loads(environ["wsgi.input"].read(size) or b"{}")
            asyncio.run(_process(payload))
        except Exception:
            # Қате болса да 200 қайтарамыз — әйтпесе Telegram сол хабарламаны қайта-қайта жібере береді
            log.exception("Update өңдеу кезінде қате")
        return _respond(start_response, "200 OK", "ok")

    return _respond(start_response, "200 OK", "Beauty Shop bot is running ✅")


async def set_webhook(url: str) -> None:
    bot = shop.make_bot()
    try:
        await bot.set_webhook(url, secret_token=webhook_secret(), drop_pending_updates=False,
                              allowed_updates=["message", "callback_query"])
        info = await bot.get_webhook_info()
        me = await bot.get_me()
        print(f"✅ Webhook орнатылды: @{me.username} → {info.url}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    import sys

    asyncio.run(set_webhook(sys.argv[1]))
