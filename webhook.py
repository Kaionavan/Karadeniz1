import json, os, urllib.request
from http.server import BaseHTTPRequestHandler

TOKEN    = os.environ.get("KARADENIZ_TOKEN", "")
ADMIN_ID    = int(os.environ.get("KARADENIZ_ADMIN", "7732138103"))
MINI_APP_URL = os.environ.get("KARADENIZ_MINIAPP", "")
API      = f"https://api.telegram.org/bot{TOKEN}"

MENU = {
    "🥗 Салаты": [
        ("Shakarob", 25000), ("Салат Оливье", 52000), ("Caprese salatasi", 72000),
        ("Yunan salatasi", 75000), ("Karadeniz salatasi", 75000),
        ("Sezar salatasi", 75000), ("Burrata salatasi", 75000), ("Çoban salatasi", 55000),
    ],
    "🥙 Кебабы": [
        ("Domatesli kebap", 79000), ("Urfa kebap", 79000), ("Adana kebap", 79000),
        ("Beyti sarma", 95000), ("Kuzu şiş", 95000), ("Tavuk şiş", 85000),
        ("1 kişilik kebap", 255000), ("4 kişilik kebap", 666000),
    ],
    "🥩 Стейки": [
        ("T-Bone Steak", 285000), ("Dallas Steak", 285000),
        ("Rib-Eye Steak", 215000), ("New York Steak", 215000),
        ("Filet Mignon", 205000), ("Lokum Steak", 205000),
    ],
    "🍝 Горячие блюда": [
        ("Güveç kavurma", 135000), ("Tavuk sate", 75000), ("Et sate", 105000),
        ("Sac tava", 115000), ("Manti porsiya", 55000), ("Norin", 55000),
        ("Pasta Bolognese", 85000), ("Pasta Alfredo", 85000),
    ],
    "🍣 Суши и Роллы": [
        ("Tempura losos", 72000), ("Filadelfia", 105000),
        ("Tempura tovuq", 68000), ("Kaliforniya", 72000),
        ("Cheddar roll", 68000), ("Karadeniz nabori", 295000),
    ],
    "🍕 Пиде и Пицца": [
        ("Karadeniz pidesi", 65000), ("Kavurmalı pide", 85000),
        ("Pizza Pepperoni", 65000), ("Pizza Mix", 78000),
        ("Pizza Karadeniz", 78000), ("Pizza Quattro Formaggi", 65000),
    ],
    "🐟 Морепродукты": [
        ("Somon balığı", 225000), ("Levrek balığı", 175000),
        ("Dorado balığı", 175000), ("Kremali karides", 125000), ("Hamsa", 85000),
    ],
    "🍰 Десерты": [
        ("Klasik baklava", 20000), ("Sütlü baklava", 27000),
        ("Trileçe", 25000), ("Künefe", 75000), ("Katmer", 105000),
        ("San Sebastian", 55000), ("Ahududulu cheesecake", 49000),
    ],
    "☕ Напитки": [
        ("Americano", 31000), ("Cappuccino", 31000), ("Latte", 31000),
        ("Türk kahvesi", 35000), ("Karadeniz çayı", 45000),
        ("Klasik milkshake", 55000), ("Klasik mojito", 35000),
    ],
}

def tg(method, **kw):
    req = urllib.request.Request(
        f"{API}/{method}",
        data=json.dumps(kw).encode(),
        headers={"Content-Type":"application/json"})
    try: urllib.request.urlopen(req, timeout=5)
    except Exception as e: print(f"TG [{method}]: {e}")

def send(cid, text, kb=None):
    kw = dict(chat_id=cid, text=text, parse_mode="Markdown")
    if kb: kw["reply_markup"] = json.dumps(kb)
    tg("sendMessage", **kw)

def edit(cid, mid, text, kb=None):
    kw = dict(chat_id=cid, message_id=mid, text=text, parse_mode="Markdown")
    if kb: kw["reply_markup"] = json.dumps(kb)
    tg("editMessageText", **kw)

def answer(cq): tg("answerCallbackQuery", callback_query_id=cq)

def kb_main():
    return {"inline_keyboard": [
        [{"text":"🍽 Меню",           "callback_data":"menu"},
         {"text":"📍 Адрес",          "callback_data":"address"}],
        [{"text":"🕐 Часы работы",    "callback_data":"hours"},
         {"text":"📞 Контакты",       "callback_data":"contacts"}],
        [{"text":"🎯 Забронировать стол", "callback_data":"book"}],
        [{"text":"📱 Открыть меню", "web_app":{"url":MINI_APP_URL}}] if MINI_APP_URL else [],
    ]}

def kb_cats():
    cats = list(MENU.keys())
    rows = [[{"text":cats[i],"callback_data":f"cat_{i}"}] +
            ([{"text":cats[i+1],"callback_data":f"cat_{i+1}"}] if i+1<len(cats) else [])
            for i in range(0,len(cats),2)]
    rows.append([{"text":"◀️ Назад","callback_data":"main"}])
    return {"inline_keyboard": rows}

def kb_back(to):
    label = "◀️ К категориям" if to=="menu" else "◀️ Назад"
    return {"inline_keyboard":[[{"text":label,"callback_data":to}]]}

def welcome(name):
    return (
        f"Assalomu alaykum, *{name}*! 👋\n\n"
        f"🌿 *KARADENIZ RESTAURANT*га хуш келибсиз!\n\n"
        f"حلال *HALAL* ✅\n\n"
        f"Турецкая и восточная кухня в самом сердце Ташкента.\n"
        f"Что вас интересует? 👇"
    )

def on_start(uid, name, cid):
    send(ADMIN_ID, f"👤 Новый гость: *{name}* (`{uid}`)")
    send(cid, welcome(name), kb_main())

def on_cb(uid, cid, mid, data, cq, name):
    answer(cq)
    if data == "main":
        edit(cid, mid, welcome(name), kb_main())
    elif data == "menu":
        edit(cid, mid, "🍽 *Меню KARADENIZ*\n\nВыберите категорию:", kb_cats())
    elif data.startswith("cat_"):
        idx = int(data[4:])
        cats = list(MENU.keys())
        if idx >= len(cats): return
        cat = cats[idx]
        lines = f"{cat}\n\n"
        for n, p in MENU[cat]:
            lines += f"• *{n}* — {p:,} сум\n"
        edit(cid, mid, lines, kb_back("menu"))
    elif data == "address":
        edit(cid, mid,
             "📍 *Адрес*\n\n"
             "Shota Rustaveli ko'chasi 69\n"
             "100070, Toshkent\n\n"
             "_Открыто каждый день 09:00–23:00_",
             {"inline_keyboard":[
                 [{"text":"🗺 Открыть на карте","url":"https://maps.google.com/?q=41.2995,69.2401"}],
                 [{"text":"◀️ Назад","callback_data":"main"}],
             ]})
    elif data == "hours":
        edit(cid, mid,
             "🕐 *Часы работы*\n\n"
             "📅 Понедельник – Воскресенье\n"
             "⏰ *09:00 – 23:00*\n\n"
             "Мы открыты каждый день! 🎉",
             kb_back("main"))
    elif data == "contacts":
        edit(cid, mid,
             "📞 *Контакты*\n\n"
             "📸 Instagram: @karadeniz.uz\n"
             "🌐 Сайт: karadeniz.uz\n"
             "📍 Shota Rustaveli 69, Tashkent\n\n"
             "حلال HALAL ✅",
             {"inline_keyboard":[
                 [{"text":"📸 Instagram","url":"https://instagram.com/karadeniz.uz"}],
                 [{"text":"🌐 karadeniz.uz","url":"https://karadeniz.uz"}],
                 [{"text":"◀️ Назад","callback_data":"main"}],
             ]})
    elif data == "book":
        send(cid,
             "🎯 *Бронирование стола*\n\n"
             "Напишите нам:\n"
             "• Дата и время\n"
             "• Количество гостей\n"
             "• Ваше имя\n\n"
             "_Мы подтвердим бронь в течение нескольких минут_ ✅")

def on_msg(uid, cid, text, name):
    if any(w in text.lower() for w in ["брон","стол","резерв","book","заброн"]):
        send(ADMIN_ID,
             f"🎯 *Бронирование!*\n👤 {name} (`{uid}`)\n📝 {text}")
        send(cid,
             "✅ *Заявка принята!*\n\n"
             "Мы свяжемся с вами для подтверждения брони 🙏",
             kb_back("main"))
    else:
        send(cid, welcome(name), kb_main())

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))))
        try:
            if "callback_query" in body:
                cq = body["callback_query"]
                on_cb(cq["from"]["id"], cq["message"]["chat"]["id"],
                      cq["message"]["message_id"], cq["data"], cq["id"],
                      cq["from"].get("first_name","Гость"))
            elif "message" in body:
                m = body["message"]
                uid, cid = m["from"]["id"], m["chat"]["id"]
                text = m.get("text","")
                name = m["from"].get("first_name","Гость")
                if text.startswith("/start"): on_start(uid, name, cid)
                else: on_msg(uid, cid, text, name)
        except Exception as e: print(f"Err: {e}")
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Karadeniz Bot alive!")
    def log_message(self, *a): pass
