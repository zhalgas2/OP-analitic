"""Beauty дүкенінің Telegram боты.

Мүмкіндіктері:
  • Каталог: санаттар → тауарлар → тауар карточкасы (сурет, сипаттама, баға)
  • Себет: санын өзгерту, тазалау, жалпы сома
  • Тапсырыс: аты → телефон → жеткізу түрі → мекенжай → түсініктеме → растау
  • Админге жаңа тапсырыс туралы хабарлама + статусты батырмамен өзгерту
    (клиентке статус автоматты түрде жіберіледі)
  • /orders — админге соңғы тапсырыстар, /myid — өз chat id-іңізді білу

Іске қосу:  BOT_TOKEN=... ADMIN_IDS=123456789 python bot.py
"""

import asyncio
import html
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

BASE_DIR = Path(__file__).resolve().parent
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x}
DB_PATH = os.getenv("BOT_DB_PATH", str(BASE_DIR / "shop.db"))
CATALOG_PATH = os.getenv("CATALOG_PATH", str(BASE_DIR / "products.json"))

log = logging.getLogger("beauty_bot")

# ───────────────────────── Каталог ─────────────────────────

with open(CATALOG_PATH, encoding="utf-8") as f:
    CATALOG = json.load(f)

SHOP = CATALOG.get("shop_name", "Beauty Shop")
CUR = CATALOG.get("currency", "₸")
CATEGORIES = {c["id"]: c for c in CATALOG["categories"]}
PRODUCTS = {p["id"]: p for p in CATALOG["products"]}
DELIVERY = {d["id"]: d for d in CATALOG["delivery"]["options"]}
FREE_FROM = CATALOG["delivery"].get("free_from") or 0

STATUSES = {
    "new": "🆕 Жаңа",
    "accepted": "✅ Қабылданды",
    "shipped": "🚚 Жолда",
    "done": "🎉 Жеткізілді",
    "canceled": "❌ Бас тартылды",
}


def money(n: int) -> str:
    return f"{n:,}".replace(",", " ") + f" {CUR}"


def e(s) -> str:
    return html.escape(str(s or ""))


# ───────────────────────── Дерекқор ─────────────────────────

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS cart (
                user_id INTEGER, product_id TEXT, qty INTEGER,
                PRIMARY KEY (user_id, product_id)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, username TEXT, name TEXT, phone TEXT,
                delivery TEXT, address TEXT, comment TEXT,
                items TEXT, subtotal INTEGER, delivery_price INTEGER, total INTEGER,
                status TEXT, created_at TEXT
            );
            """
        )


def cart_get(uid: int) -> list[tuple[dict, int]]:
    with db() as con:
        rows = con.execute("SELECT product_id, qty FROM cart WHERE user_id=?", (uid,)).fetchall()
    return [(PRODUCTS[r["product_id"]], r["qty"]) for r in rows if r["product_id"] in PRODUCTS]


def cart_change(uid: int, pid: str, delta: int) -> int:
    with db() as con:
        row = con.execute("SELECT qty FROM cart WHERE user_id=? AND product_id=?", (uid, pid)).fetchone()
        qty = (row["qty"] if row else 0) + delta
        if qty <= 0:
            con.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (uid, pid))
            return 0
        qty = min(qty, 99)
        con.execute("INSERT OR REPLACE INTO cart VALUES (?,?,?)", (uid, pid, qty))
        return qty


def cart_clear(uid: int):
    with db() as con:
        con.execute("DELETE FROM cart WHERE user_id=?", (uid,))


def cart_subtotal(items) -> int:
    return sum(p["price"] * q for p, q in items)


def delivery_price(did: str, subtotal: int) -> int:
    price = DELIVERY[did]["price"]
    return 0 if FREE_FROM and subtotal >= FREE_FROM else price


# ───────────────────────── Пернетақталар ─────────────────────────

BTN_CATALOG = "🛍 Каталог"
BTN_CART = "🛒 Себет"
BTN_ORDERS = "📦 Тапсырыстарым"
BTN_CONTACTS = "📞 Байланыс"
BTN_CANCEL = "❌ Болдырмау"

MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BTN_CATALOG), KeyboardButton(text=BTN_CART)],
              [KeyboardButton(text=BTN_ORDERS), KeyboardButton(text=BTN_CONTACTS)]],
    resize_keyboard=True,
)
CANCEL_KB = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_CANCEL)]], resize_keyboard=True)
PHONE_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Нөмірімді жіберу", request_contact=True)],
              [KeyboardButton(text=BTN_CANCEL)]],
    resize_keyboard=True,
)


def ikb(rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d) for t, d in row] for row in rows]
    )


def categories_kb():
    return ikb([[(c["title"], f"cat:{c['id']}")] for c in CATALOG["categories"]])


def products_kb(cid: str):
    rows = [[(f"{p['name']} — {money(p['price'])}", f"prod:{p['id']}")]
            for p in CATALOG["products"] if p["category"] == cid]
    rows.append([("⬅️ Санаттар", "cats"), (BTN_CART, "cart")])
    return ikb(rows)


def product_kb(p: dict, qty: int):
    rows = []
    if qty:
        rows.append([("➖", f"pdec:{p['id']}"), (f"Себетте: {qty} дана", "noop"), ("➕", f"pinc:{p['id']}")])
    else:
        rows.append([("🛒 Себетке қосу", f"pinc:{p['id']}")])
    rows.append([("⬅️ Артқа", f"cat:{p['category']}"), (BTN_CART, "cart")])
    return ikb(rows)


def product_text(p: dict) -> str:
    return f"<b>{e(p['name'])}</b>\n\n{e(p.get('description'))}\n\n💰 <b>{money(p['price'])}</b>"


def cart_view(uid: int):
    items = cart_get(uid)
    if not items:
        return "🛒 Себетіңіз бос.\n\nКаталогтан тауар таңдаңыз 👇", ikb([[("🛍 Каталог", "cats")]])
    lines = [f"🛒 <b>Сіздің себетіңіз</b>\n"]
    rows = []
    for p, q in items:
        lines.append(f"• {e(p['name'])}\n   {q} × {money(p['price'])} = <b>{money(p['price'] * q)}</b>")
        rows.append([("➖", f"cdec:{p['id']}"), (f"{p['name'][:22]} ({q})", "noop"), ("➕", f"cinc:{p['id']}")])
    sub = cart_subtotal(items)
    lines.append(f"\nЖиыны: <b>{money(sub)}</b>")
    if FREE_FROM:
        lines.append("🎁 Жеткізу тегін!" if sub >= FREE_FROM
                     else f"🎁 Тегін жеткізуге дейін: {money(FREE_FROM - sub)}")
    rows.append([("🗑 Тазалау", "cclear"), ("🛍 Жалғастыру", "cats")])
    rows.append([("✅ Тапсырыс беру", "checkout")])
    return "\n".join(lines), ikb(rows)


def order_text(o, for_admin=False) -> str:
    items = json.loads(o["items"])
    lines = [f"🧾 <b>Тапсырыс №{o['id']}</b> — {STATUSES.get(o['status'], o['status'])}",
             f"🕒 {o['created_at']}\n"]
    for it in items:
        lines.append(f"• {e(it['name'])} — {it['qty']} × {money(it['price'])}")
    lines.append(f"\nТауарлар: {money(o['subtotal'])}")
    lines.append(f"Жеткізу: {e(DELIVERY.get(o['delivery'], {}).get('title', o['delivery']))} — "
                 f"{money(o['delivery_price']) if o['delivery_price'] else 'тегін'}")
    lines.append(f"<b>Барлығы: {money(o['total'])}</b>\n")
    lines.append(f"👤 {e(o['name'])}\n📱 {e(o['phone'])}")
    if o["address"]:
        lines.append(f"📍 {e(o['address'])}")
    if o["comment"]:
        lines.append(f"💬 {e(o['comment'])}")
    if for_admin:
        uname = f"@{e(o['username'])}" if o["username"] else "username жоқ"
        lines.append(f"\n🔗 <a href=\"tg://user?id={o['user_id']}\">Клиентке жазу</a> ({uname})")
    return "\n".join(lines)


def admin_order_kb(oid: int):
    return ikb([
        [("✅ Қабылдау", f"st:{oid}:accepted"), ("🚚 Жолда", f"st:{oid}:shipped")],
        [("🎉 Жеткізілді", f"st:{oid}:done"), ("❌ Бас тарту", f"st:{oid}:canceled")],
    ])


# ───────────────────────── Хэндлерлер ─────────────────────────

router = Router()


class Checkout(StatesGroup):
    name = State()
    phone = State()
    delivery = State()
    address = State()
    comment = State()
    confirm = State()


async def show(cb: CallbackQuery, text: str, kb: InlineKeyboardMarkup):
    """Хабарламаны орнында ауыстырады; суретті хабарлама болса — өшіріп, жаңасын жібереді."""
    if cb.message.photo:
        await cb.message.delete()
        await cb.message.answer(text, reply_markup=kb)
    else:
        await cb.message.edit_text(text, reply_markup=kb)


@router.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(
        f"Сәлеметсіз бе, {e(m.from_user.first_name)}! 🌸\n\n"
        f"<b>{e(SHOP)}</b> дүкеніне қош келдіңіз.\n"
        "Мұнда бетке, шашқа, денеге күтім құралдары мен макияж тауарларын тапсырыс бере аласыз.\n\n"
        "Төмендегі мәзірді қолданыңыз 👇",
        reply_markup=MAIN_KB,
    )


@router.message(Command("myid"))
async def myid(m: Message):
    await m.answer(f"Сіздің chat id: <code>{m.chat.id}</code>")


@router.message(StateFilter("*"), F.text == BTN_CANCEL)
@router.message(StateFilter("*"), Command("cancel"))
async def cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Тапсырыс беру тоқтатылды. Себетіңіз сақталды.", reply_markup=MAIN_KB)


@router.message(F.text == BTN_CATALOG)
@router.message(Command("catalog"))
async def catalog(m: Message):
    await m.answer("🛍 <b>Санатты таңдаңыз:</b>", reply_markup=categories_kb())


@router.callback_query(F.data == "cats")
async def cb_cats(cb: CallbackQuery):
    await show(cb, "🛍 <b>Санатты таңдаңыз:</b>", categories_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(cb: CallbackQuery):
    cid = cb.data.split(":", 1)[1]
    cat = CATEGORIES.get(cid)
    if not cat:
        return await cb.answer("Санат табылмады", show_alert=True)
    await show(cb, f"<b>{e(cat['title'])}</b>\n\nТауарды таңдаңыз:", products_kb(cid))
    await cb.answer()


async def send_product(cb: CallbackQuery, p: dict):
    qty = next((q for pp, q in cart_get(cb.from_user.id) if pp["id"] == p["id"]), 0)
    kb = product_kb(p, qty)
    if p.get("photo"):
        await cb.message.delete()
        await cb.message.answer_photo(p["photo"], caption=product_text(p), reply_markup=kb)
    else:
        await show(cb, product_text(p), kb)


@router.callback_query(F.data.startswith("prod:"))
async def cb_product(cb: CallbackQuery):
    p = PRODUCTS.get(cb.data.split(":", 1)[1])
    if not p:
        return await cb.answer("Тауар табылмады", show_alert=True)
    await send_product(cb, p)
    await cb.answer()


@router.callback_query(F.data.regexp(r"^p(inc|dec):"))
async def cb_product_qty(cb: CallbackQuery):
    action, pid = cb.data.split(":", 1)
    p = PRODUCTS.get(pid)
    if not p:
        return await cb.answer("Тауар табылмады", show_alert=True)
    qty = cart_change(cb.from_user.id, pid, 1 if action == "pinc" else -1)
    await cb.message.edit_reply_markup(reply_markup=product_kb(p, qty))
    await cb.answer("Себетке қосылды ✅" if action == "pinc" else "Себеттен азайтылды")


@router.message(F.text == BTN_CART)
@router.message(Command("cart"))
async def cart(m: Message):
    text, kb = cart_view(m.from_user.id)
    await m.answer(text, reply_markup=kb)


@router.callback_query(F.data == "cart")
async def cb_cart(cb: CallbackQuery):
    text, kb = cart_view(cb.from_user.id)
    await show(cb, text, kb)
    await cb.answer()


@router.callback_query(F.data.regexp(r"^c(inc|dec):"))
async def cb_cart_qty(cb: CallbackQuery):
    action, pid = cb.data.split(":", 1)
    if pid in PRODUCTS:
        cart_change(cb.from_user.id, pid, 1 if action == "cinc" else -1)
    text, kb = cart_view(cb.from_user.id)
    await show(cb, text, kb)
    await cb.answer()


@router.callback_query(F.data == "cclear")
async def cb_cart_clear(cb: CallbackQuery):
    cart_clear(cb.from_user.id)
    text, kb = cart_view(cb.from_user.id)
    await show(cb, text, kb)
    await cb.answer("Себет тазаланды")


@router.callback_query(F.data == "noop")
async def cb_noop(cb: CallbackQuery):
    await cb.answer()


@router.message(F.text == BTN_CONTACTS)
async def contacts(m: Message):
    c = CATALOG.get("contacts", {})
    rows = []
    if c.get("whatsapp"):
        rows.append([InlineKeyboardButton(text="💬 WhatsApp", url=c["whatsapp"])])
    if c.get("instagram"):
        rows.append([InlineKeyboardButton(text="📸 Instagram", url=c["instagram"])])
    await m.answer(
        f"📞 <b>{e(SHOP)}</b>\n\n"
        f"Телефон: {e(c.get('phone'))}\n📍 {e(c.get('address'))}\n🕒 {e(c.get('hours'))}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows) if rows else None,
    )


@router.message(F.text == BTN_ORDERS)
async def my_orders(m: Message):
    with db() as con:
        rows = con.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 5",
                           (m.from_user.id,)).fetchall()
    if not rows:
        return await m.answer("Сізде әлі тапсырыс жоқ. 🛍 Каталогтан бастаңыз!")
    await m.answer("\n\n".join(
        f"🧾 №{o['id']} · {o['created_at'][:10]} · {money(o['total'])}\n{STATUSES.get(o['status'], o['status'])}"
        for o in rows))


# ── Тапсырыс беру ──

@router.callback_query(F.data == "checkout")
async def cb_checkout(cb: CallbackQuery, state: FSMContext):
    if not cart_get(cb.from_user.id):
        return await cb.answer("Себет бос", show_alert=True)
    await cb.answer()
    await state.set_state(Checkout.name)
    await cb.message.answer("✍️ Атыңызды жазыңыз:", reply_markup=CANCEL_KB)


@router.message(Checkout.name, F.text)
async def co_name(m: Message, state: FSMContext):
    name = m.text.strip()[:60]
    if len(name) < 2:
        return await m.answer("Атыңызды толығырақ жазыңыз:")
    await state.update_data(name=name)
    await state.set_state(Checkout.phone)
    await m.answer("📱 Телефон нөміріңізді жіберіңіз (батырманы басыңыз немесе жазыңыз):", reply_markup=PHONE_KB)


@router.message(Checkout.phone)
async def co_phone(m: Message, state: FSMContext):
    phone = m.contact.phone_number if m.contact else (m.text or "").strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 10:
        return await m.answer("Нөмір дұрыс емес сияқты. Мысалы: +7 701 123 45 67")
    await state.update_data(phone=phone if phone.startswith("+") else f"+{digits}")
    await state.set_state(Checkout.delivery)
    await m.answer("Жақсы 👍", reply_markup=CANCEL_KB)
    sub = cart_subtotal(cart_get(m.from_user.id))
    await m.answer("🚚 Жеткізу түрін таңдаңыз:", reply_markup=ikb(
        [[(f"{d['title']} — {money(delivery_price(d['id'], sub)) if delivery_price(d['id'], sub) else 'тегін'}",
           f"dl:{d['id']}")] for d in CATALOG["delivery"]["options"]]))


@router.callback_query(Checkout.delivery, F.data.startswith("dl:"))
async def co_delivery(cb: CallbackQuery, state: FSMContext):
    did = cb.data.split(":", 1)[1]
    if did not in DELIVERY:
        return await cb.answer()
    await state.update_data(delivery=did)
    await cb.message.edit_text(f"🚚 Жеткізу: {e(DELIVERY[did]['title'])}")
    await cb.answer()
    if did == "pickup":
        await state.update_data(address="")
        await state.set_state(Checkout.comment)
        await cb.message.answer("💬 Түсініктеме бар ма? Жоқ болса «-» деп жазыңыз.")
    else:
        await state.set_state(Checkout.address)
        await cb.message.answer("📍 Жеткізу мекенжайын жазыңыз (қала, көше, үй, пәтер):")


@router.message(Checkout.address, F.text)
async def co_address(m: Message, state: FSMContext):
    if len(m.text.strip()) < 5:
        return await m.answer("Мекенжайды толығырақ жазыңыз:")
    await state.update_data(address=m.text.strip()[:300])
    await state.set_state(Checkout.comment)
    await m.answer("💬 Түсініктеме бар ма? Жоқ болса «-» деп жазыңыз.")


@router.message(Checkout.comment, F.text)
async def co_comment(m: Message, state: FSMContext):
    comment = "" if m.text.strip() in {"-", "—", "жоқ", "Жоқ"} else m.text.strip()[:500]
    await state.update_data(comment=comment)
    data = await state.get_data()
    items = cart_get(m.from_user.id)
    if not items:
        await state.clear()
        return await m.answer("Себет бос.", reply_markup=MAIN_KB)
    sub = cart_subtotal(items)
    dp = delivery_price(data["delivery"], sub)
    preview = {
        "id": "—", "status": "new", "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "items": json.dumps([{"name": p["name"], "qty": q, "price": p["price"]} for p, q in items]),
        "subtotal": sub, "delivery_price": dp, "total": sub + dp, "delivery": data["delivery"],
        "name": data["name"], "phone": data["phone"], "address": data["address"], "comment": comment,
    }
    await state.set_state(Checkout.confirm)
    await m.answer("Тексеріңіз 👇", reply_markup=MAIN_KB)
    await m.answer(order_text(preview).replace("Тапсырыс №—", "Тапсырысыңыз"),
                   reply_markup=ikb([[("✅ Растау", "co:ok"), ("❌ Болдырмау", "co:no")]]))


@router.callback_query(Checkout.confirm, F.data == "co:no")
async def co_no(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Тапсырыс болдырылмады. Себетіңіз сақталды 🛒")
    await cb.answer()


@router.callback_query(Checkout.confirm, F.data == "co:ok")
async def co_ok(cb: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    items = cart_get(cb.from_user.id)
    if not items:
        await state.clear()
        return await cb.answer("Себет бос", show_alert=True)
    sub = cart_subtotal(items)
    dp = delivery_price(data["delivery"], sub)
    with db() as con:
        cur = con.execute(
            "INSERT INTO orders (user_id, username, name, phone, delivery, address, comment, items,"
            " subtotal, delivery_price, total, status, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cb.from_user.id, cb.from_user.username or "", data["name"], data["phone"], data["delivery"],
             data["address"], data["comment"],
             json.dumps([{"id": p["id"], "name": p["name"], "qty": q, "price": p["price"]} for p, q in items],
                        ensure_ascii=False),
             sub, dp, sub + dp, "new", datetime.now().strftime("%d.%m.%Y %H:%M")),
        )
        oid = cur.lastrowid
        order = con.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
    cart_clear(cb.from_user.id)
    await state.clear()
    await cb.message.edit_text(
        f"🎉 <b>Рахмет! Тапсырысыңыз №{oid} қабылданды.</b>\n\n"
        "Менеджер жақын арада сізбен байланысады. Статус өзгерсе, осы жерге хабарлама келеді.")
    await cb.answer()
    for admin in ADMIN_IDS:
        try:
            await bot.send_message(admin, order_text(order, for_admin=True), reply_markup=admin_order_kb(oid))
        except Exception as err:  # админ ботты бастамаған болуы мүмкін
            log.warning("Админге жіберілмеді %s: %s", admin, err)


# ── Админ ──

@router.callback_query(F.data.startswith("st:"))
async def cb_status(cb: CallbackQuery, bot: Bot):
    if cb.from_user.id not in ADMIN_IDS:
        return await cb.answer("Рұқсат жоқ", show_alert=True)
    _, oid, st = cb.data.split(":")
    if st not in STATUSES:
        return await cb.answer()
    with db() as con:
        con.execute("UPDATE orders SET status=? WHERE id=?", (st, int(oid)))
        o = con.execute("SELECT * FROM orders WHERE id=?", (int(oid),)).fetchone()
    if not o:
        return await cb.answer("Тапсырыс табылмады", show_alert=True)
    await cb.message.edit_text(order_text(o, for_admin=True), reply_markup=admin_order_kb(o["id"]))
    await cb.answer(f"Статус: {STATUSES[st]}")
    try:
        await bot.send_message(o["user_id"], f"🧾 Тапсырыс №{o['id']} статусы: <b>{STATUSES[st]}</b>")
    except Exception as err:
        log.warning("Клиентке жіберілмеді %s: %s", o["user_id"], err)


@router.message(Command("orders"))
async def admin_orders(m: Message):
    if m.from_user.id not in ADMIN_IDS:
        return
    with db() as con:
        rows = con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 10").fetchall()
    if not rows:
        return await m.answer("Тапсырыс әлі жоқ.")
    for o in reversed(rows):
        await m.answer(order_text(o, for_admin=True), reply_markup=admin_order_kb(o["id"]))


@router.message(StateFilter(Checkout.name, Checkout.address, Checkout.comment))
async def need_text(m: Message):
    await m.answer("Мәтінмен жазыңыз немесе «❌ Болдырмау» басыңыз.")


@router.message()
async def fallback(m: Message):
    await m.answer("Төмендегі мәзірді қолданыңыз 👇", reply_markup=MAIN_KB)


# ───────────────────────── Іске қосу ─────────────────────────

def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    return dp


async def main():
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN орнатылмаған. @BotFather-ден токен алып, BOT_TOKEN айнымалысына жазыңыз.")
    if not ADMIN_IDS:
        log.warning("ADMIN_IDS бос — тапсырыстар ешкімге жіберілмейді. /myid арқылы id-іңізді біліңіз.")
    init_db()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=False)
    await build_dispatcher().start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
