import asyncio, requests, re, random, string, json, os, time, base64
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, BusinessConnectionHandler,
    MessageHandler, filters, CallbackQueryHandler, TypeHandler
)
import urllib.parse

# ---------- НАСТРОЙКИ (замените на свои) ----------
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
PEXELS_API_KEY = "wMLd461WhqbSiDPkaHXtieu2UfuFcJXqB1CfqMb9wJTOr60VnUExeTQP"  # ваш ключ Pexels
# -------------------------------------------------

# API endpoints
TIKTOK_API = "https://tikwm.com/api/"
WEATHER_API = "https://wttr.in/"
TRANSLATE_API = "https://translate.googleapis.com/translate_a/single"
JOKE_API = "https://v2.jokeapi.dev/joke/Any"
FACT_API = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
QUOTE_API = "https://api.quotable.io/random"
QR_API = "https://api.qrserver.com/v1/create-qr-code/"
CAT_API = "https://api.thecatapi.com/v1/images/search"
DOG_API = "https://api.thedogapi.com/v1/images/search"
TIME_API = "http://worldtimeapi.org/api/timezone"
WIKI_API = "https://ru.wikipedia.org/api/rest_v1/page/summary/"

# ==================== ПЕРЕВОДЧИК (Google Translate) ====================
def google_translate(text, source, target):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {'client': 'gtx', 'sl': source, 'tl': target, 'dt': 't', 'q': text}
    full_url = url + '?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(full_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            translated = ''.join([part[0] for part in data[0] if part[0]])
            return translated
    except:
        return text

# ==================== Файлы и переменные ====================
SETTINGS_FILE = "user_settings.json"
try:
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        user_settings = json.load(f)
except:
    user_settings = {}

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(user_settings, f, indent=2, ensure_ascii=False)

user_limits = {}
auto_trolls = {}
active_games = {}
message_cache = {}
business_owners = {}
business_connections = {}
conn_owners = {}

TROLL_PHRASES = [
    "ТЫ ПОНИМАЕШЬ ЧТО Я ПИЗДАК ВТЕОЙ МАТРЕИ НА СВОЙ УЙ КАК МАКАРОНИНУ НАМОТАЛ БЛЯДЬ И НАЧАЛ РАСКРУЧИВАТЬ ЕЁ, ПОСЛЕ ЧЕГО ВЫКИНУЛ В КОСМОС, ЧТОБ ЕЁ ТАМ ИНОПЛАНЕТЯНЫ ХУЯМИ РВАЛИ",
    "ТЫ ПОНИМАЕШЬ ЧТО Я ТВОЮ МАТЬ ОТПРАВИЛ СО СВОЕГО ЪХУЯ В НЕБО, ЧТОБ ОНА СВОИМ ПИЗДАКОМ ПРИНИМАЛА МИТЕОРИТНУЮ АТАКУ?",
    "ТЫ ПОНИМАЕШЬ ЧТО Я ВО ВРЕМЯ ХОККЕЙНОГО МАТЧА, ТВОЮ МАТЬ ВЫИКНУЛ НАХУЙ НА ПЛОЩАДКУ, ЧТОБ ОНА ПИЗДАКОМ СВОИМ ВОРОТА РУССКИХ ЗАЩИЩАЛА",
    "дефайся с хуем во рту до и после каких слов тебе маму ебали все ты я не твоя мама",
    "понял тебя хуесос терпи мой член",
    "окей что ты в надгробие отца сказал во всех провокации не было ни сказок, легенд, фантазии, миров, снов, обманов, кличек, погонял, фраз, галактики, вселенной, примечание, и всего такого",
    "задай вопрос своему факеру кто как и чем и где ебал тя когда ты был в биологическом теле своей матери в прямом дне в обычном мире ?",
    "на пенисяку говори",
    "в зеркало че",
    "на пенис че",
    "рассуждение в хуй",
    "описание себя в хуй все ты",
    "в хуяку чевсе ты деф в хуй",
    "оправдание в хуй",
    "проблема бабки",
    "фантазируй на член",
    "самокоманду в хуй",
    "все ты скажи что ты пидор оправданием после минета ртом отца гея",
    "че деду с хуя после минета отвечай все ты",
    "маму тебе ебали со словами какими в зеркало фантазируй",
    "опиши как маму твою ебали",
    "после хуя отцу хуесосу расскажи",
    "с какой такой провокацией тебя ебали в рот и в жопу",
    "сказку в хуй все ты",
    "че в зеркальный дик все ты",
    "кто харкал",
    "что делал языком ты",
    "выскажись в хуй языком по пенису опять",
    "оправдайся языком по пенису",
    "представление в дик ниже",
    "голос подай с хуя ебырю членовому своему",
    "обратись к семье",
    "обстоятельства при минете ниже расскажи",
    "вообрази ник факера мои слова не считаются",
    "вообрази что ебал жопой и ртом своим",
    "перескажи слова свои после минета",
    "оправдайся кто маму твою ебал скажи после минета все ники твои у всех",
    "сосешь словом каким",
    "нафантазируй жопой своей скрины в хуй текст в хуй ниже в хуй",
    "отпиши ниже в пенис и отсоси его",
    "убей бабку буквой от и до все буквы твои в тебя",
    "до и после твоих слов и прок ты сакал чем если все ты",
    "языком по жопе ты че",
    "кто ебал тебя если я твой членовой ебырь",
    "отрицай в хуяку педик все ты",
    "зашифруй с хуя фантазией в дик",
    "что мне твоя мама шлюха в зеркало сидя на пенисе я не твоя мама",
    "переводи себя и говори в хуй",
    "с каким таким представлением ты пенис сакал",
    "представь в зеркало ниже",
    "все что ты скажешь на хуе покажешь поехали",
    "с какими такими словами мать твою ебал твой членовой ебырь",
    "какими такими словами маму твою резали под запись поехали",
    "в зеркальном мире что ты говорил реще пиши в хуй поехали",
    "кто твоя мамка кроме сакерши все ты ниже соври мое не считается",
    "до и после твои слова мифы представление в хуй кидай ниже",
    "обмани бабку хуем в рот когда ты в зеркальной будке и все не пробиваемое",
    "какими такими словами ты сидя на пенисе одновременно ловил хуи в рот все ты",
    "до и после ты чем сакал кроме рта матери своей все ты ты в зеркальном ворлде",
    "убей батю со словами кроме молчания в хуяку представь ниже",
    "соври с пениса и в пенис сидя на нем говоря ртом отца гея все ты",
    "подтверди что ты хуесос ниже сидя на пенисе говори факеру своему",
    "расскажи как тебя бог выебал членом",
    "до и после ебал тя в рот и после этого че ты маме сказал все ты",
]

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def search_pexels_photos(query, count=3):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": min(count, 10), "locale": "ru-RU"}
    try:
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=10)
        data = resp.json()
        photos = []
        if "photos" in data:
            for photo in data["photos"][:count]:
                photos.append(photo["src"]["large"])
        return photos
    except:
        return []

def rps_emoji(move):
    return {"r": "🪨", "p": "📄", "s": "✂️"}.get(move, "❓")

def rps_winner(m1, m2):
    if m1 == m2: return "draw"
    wins = {"r": "s", "s": "p", "p": "r"}
    return "win" if wins[m1] == m2 else "lose"

def format_board(board):
    symbols = {"X": "❌", "O": "⭕", " ": "⬜"}
    return "\n".join("".join(symbols[cell] for cell in row) for row in board)

def build_ttt_keyboard(board):
    keyboard = []
    for i, row in enumerate(board):
        btn_row = []
        for j, cell in enumerate(row):
            if cell == " ":
                btn_row.append(InlineKeyboardButton("⬜", callback_data=f"ttt_{i}_{j}"))
            else:
                btn_row.append(InlineKeyboardButton("❌" if cell == "X" else "⭕", callback_data="ttt_noop"))
        keyboard.append(btn_row)
    return InlineKeyboardMarkup(keyboard)

def check_ttt_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ": return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != " ": return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != " ": return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ": return board[0][2]
    return None

def is_board_full(board):
    return all(cell != " " for row in board for cell in row)

# ==================== НАСТРОЙКИ ПРОФИЛЯ ====================
TIMEZONES = {
    "Europe/Moscow": "🇷🇺 Москва (MSK)",
    "Europe/London": "🇬🇧 Лондон",
    "Europe/Berlin": "🇩🇪 Берлин",
    "Asia/Yekaterinburg": "🇷🇺 Екатеринбург",
    "Asia/Omsk": "🇷🇺 Омск",
    "Asia/Novosibirsk": "🇷🇺 Новосибирск",
    "Asia/Krasnoyarsk": "🇷🇺 Красноярск",
    "Asia/Irkutsk": "🇷🇺 Иркутск",
    "Asia/Vladivostok": "🇷🇺 Владивосток",
    "America/New_York": "🇺🇸 Нью-Йорк",
}

def get_user_settings(user_id):
    uid = str(user_id)
    if uid not in user_settings:
        user_settings[uid] = {"time_in_nick": False, "timezone": "Europe/Moscow"}
        save_settings()
    return user_settings[uid]

# ==================== ОСНОВНЫЕ ОБРАБОТЧИКИ ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я BoBmod — ваш личный чат-ассистент.\n\n"
        "Используйте .help для списка команд.\n"
        "Настройки: /settings"
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    settings = get_user_settings(user_id)
    tz_key = settings.get("timezone", "Europe/Moscow")
    tz_name = TIMEZONES.get(tz_key, tz_key)
    time_nick_status = "✅ Вкл" if settings.get("time_in_nick") else "❌ Выкл"
    text = (
        "⚙️ **Настройки профиля**\n\n"
        f"🕒 Отображение времени в нике: {time_nick_status}\n"
        f"🌍 Часовой пояс: {tz_name}\n\n"
        "Выберите действие:"
    )
    keyboard = [
        [InlineKeyboardButton("🔄 Вкл/выкл время в нике", callback_data="toggle_time_nick")],
        [InlineKeyboardButton("🌍 Сменить часовой пояс", callback_data="select_tz")],
        [InlineKeyboardButton("🔙 Закрыть", callback_data="close_settings")]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def on_business_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = update.business_connection
    owner_id = conn.user.id
    if conn.is_enabled:
        business_connections[owner_id] = conn.id
        conn_owners[conn.id] = owner_id
        try:
            await context.bot.set_business_account_bio(
                business_connection_id=conn.id,
                bio=f"User @BoBmodINFO\n{conn.user.bio or ''}"
            )
        except Exception as e:
            print(f"Ошибка установки bio: {e}")
        print(f"✅ Бизнес-подключение от {owner_id}")
    else:
        biz_id = business_connections.pop(owner_id, None)
        if biz_id:
            conn_owners.pop(biz_id, None)
        print(f"❌ Бизнес-подключение отключено {owner_id}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    user_id = user.id
    await query.answer()

    # Настройки
    if data == "toggle_time_nick":
        settings = get_user_settings(user_id)
        settings["time_in_nick"] = not settings.get("time_in_nick", False)
        save_settings()
        await query.edit_message_text(f"Отображение времени в нике: {'✅ Вкл' if settings['time_in_nick'] else '❌ Выкл'}")
    elif data == "select_tz":
        keyboard = []
        for tz, name in TIMEZONES.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"settz_{tz}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_settings")])
        await query.edit_message_text("Выберите часовой пояс:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("settz_"):
        tz = data[6:]
        settings = get_user_settings(user_id)
        settings["timezone"] = tz
        save_settings()
        await query.edit_message_text(f"Часовой пояс установлен: {TIMEZONES.get(tz, tz)}")
    elif data == "back_settings":
        await settings_command(update, context)
    elif data == "close_settings":
        await query.edit_message_text("Настройки закрыты")

    # Крестики-нолики
    elif data.startswith("ttt_"):
        chat_id = query.message.chat_id
        if chat_id not in active_games or active_games[chat_id]["game"] != "ttt":
            await query.edit_message_text("❌ Игра не найдена")
            return
        game = active_games[chat_id]
        _, row, col = data.split("_")
        row, col = int(row), int(col)
        if user_id not in game["players"]:
            await query.answer("Вы не в игре!", show_alert=True)
            return
        if game["turn"] != user_id:
            await query.answer("Не ваш ход!", show_alert=True)
            return
        if game["board"][row][col] != " ":
            await query.answer("Клетка занята!", show_alert=True)
            return
        game["board"][row][col] = game["players"][user_id]
        winner = check_ttt_winner(game["board"])
        if winner:
            await query.edit_message_text(f"🎮 Крестики-нолики\n\n{format_board(game['board'])}\n\n🎉 Победитель!", reply_markup=None)
            del active_games[chat_id]
        elif is_board_full(game["board"]):
            await query.edit_message_text(f"🎮 Крестики-нолики\n\n{format_board(game['board'])}\n\n🤝 Ничья!", reply_markup=None)
            del active_games[chat_id]
        else:
            for uid in game["players"]:
                if uid != user_id:
                    game["turn"] = uid
                    break
            await query.edit_message_text(f"🎮 Крестики-нолики\n\n{format_board(game['board'])}", reply_markup=build_ttt_keyboard(game["board"]))

    # Камень-ножницы-бумага
    elif data.startswith("rps_"):
        chat_id = query.message.chat_id
        if chat_id not in active_games or active_games[chat_id]["game"] != "rps":
            await query.edit_message_text("❌ Игра не найдена")
            return
        game = active_games[chat_id]
        if user_id not in game["moves"]:
            game["moves"][user_id] = data.split("_")[1]
            await query.answer("Принято!")
            if len(game["moves"]) == 2:
                players = list(game["moves"].keys())
                p1, p2 = players[0], players[1]
                m1, m2 = game["moves"][p1], game["moves"][p2]
                result = rps_winner(m1, m2)
                if result == "draw":
                    text = f"🤝 Ничья! {rps_emoji(m1)} vs {rps_emoji(m2)}"
                else:
                    text = f"🎮 {rps_emoji(m1)} vs {rps_emoji(m2)}\n\n🎉 Победитель!"
                await query.edit_message_text(text, reply_markup=None)
                del active_games[chat_id]
        else:
            await query.answer("Уже выбрано!", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.business_message
    if not msg or not msg.text:
        return

    chat_id = msg.chat_id
    message_id = msg.message_id

    if chat_id not in message_cache:
        message_cache[chat_id] = {}
    message_cache[chat_id][message_id] = (msg.from_user, msg.text)

    if msg.text.startswith("/start"):
        await start_command(update, context)
        return
    if msg.text.startswith("/settings"):
        await settings_command(update, context)
        return

    if not msg.business_connection_id:
        return

    owner_id = conn_owners.get(msg.business_connection_id)
    if owner_id is None:
        if msg.from_user:
            owner_id = msg.from_user.id
            conn_owners[msg.business_connection_id] = owner_id
        else:
            return

    business_owners[chat_id] = owner_id
    user_id = owner_id

    text = msg.text.strip()
    cmd = text.lower().split()[0] if text else ""
    args = text[len(cmd):].strip() if len(text) > len(cmd) else ""

    if chat_id in auto_trolls:
        target_id = auto_trolls[chat_id]
        reply_msg = msg.reply_to_message
        if reply_msg and reply_msg.from_user and reply_msg.from_user.id == target_id:
            phrase = random.choice(TROLL_PHRASES)
            await msg.reply_text(phrase)
            return

    edit_text = None
    edit_photo = None
    edit_video = None
    edit_voice = None
    edit_caption = None
    delete_and_send_new = False

    # ==================== РОУТИНГ КОМАНД ====================
    if cmd == ".help":
        edit_text = (
            "🤖 BoBmod — ваш личный ассистент\n\n"
            "📋 Основные:\n"
            ".info — инфо о собеседнике\n"
            ".save — скачать TikTok\n\n"
            "🧰 Инструменты:\n"
            ".weather .translate .calc .qr .poll .search .voice .cat .dog .time .wiki .dice .coin .password .nick\n"
            ".photo — найти фото (Pexels)\n"
            ".base64 enc/dec — кодирование Base64\n\n"
            "🎭 Текст:\n"
            ".mock .reverse .vaporwave .bold .italic\n\n"
            "💬 Действия:\n"
            ".hug .slap .pat .kill\n\n"
            "🎮 Игры:\n"
            ".rps — камень-ножницы-бумага\n"
            ".ttt — крестики-нолики\n\n"
            "🎭 Развлечения:\n"
            ".fact .joke .quote\n\n"
            "🤡 Троллинг:\n"
            ".troll .a_troll .a_troll_off\n\n"
            "🛡 Антиудаление: бот показывает удалённые сообщения в лс\n"
            "⚙️ Настройки: /settings (время в нике, часовой пояс)\n\n"
            "С уважением: @BoBmodRobot"
        )

    elif cmd == ".info":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение"
        else:
            user = msg.reply_to_message.from_user
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "—"
            premium = "⭐" if getattr(user, 'is_premium', False) else "❌"
            bot = "🤖" if getattr(user, 'is_bot', False) else "👤"
            edit_text = f"ℹ️ Информация:\n\n👤 Имя: {full_name}\n🔖 Юзернейм: {username}\n🆔 ID: {user.id}\n💎 Premium: {premium}\n🤖 Бот: {bot}"

    elif cmd == ".save":
        if not msg.reply_to_message or not msg.reply_to_message.text:
            edit_text = "❌ Ответьте на сообщение со ссылкой TikTok"
        else:
            urls = re.findall(r'https?://[^\s]+', msg.reply_to_message.text)
            if not urls:
                edit_text = "❌ Ссылка не найдена"
            else:
                tiktok_url = urls[0]
                user_id_limits = msg.from_user.id if msg.from_user else msg.chat_id
                today = datetime.now().date()
                if user_id_limits in user_limits:
                    limit_date, count = user_limits[user_id_limits]
                    if limit_date == today and count >= 5:
                        edit_text = "⏳ Лимит: 5 видео в день"
                    elif limit_date != today:
                        user_limits[user_id_limits] = [today, 0]
                if not edit_text:
                    try:
                        resp = requests.get(TIKTOK_API, params={"url": tiktok_url}, timeout=60)
                        data = resp.json()
                        if data.get("code") == 0 and data.get("data"):
                            video_url = data["data"].get("play") or data["data"].get("hdplay")
                            if video_url:
                                vresp = requests.get(video_url, timeout=120)
                                if vresp.status_code == 200:
                                    if user_id_limits not in user_limits or user_limits[user_id_limits][0] != today:
                                        user_limits[user_id_limits] = [today, 1]
                                    else:
                                        user_limits[user_id_limits][1] += 1
                                    edit_video = vresp.content
                                    edit_caption = f"✅ {data['data'].get('title', '')}\n📊 Осталось: {5 - user_limits[user_id_limits][1]}/5"
                                    delete_and_send_new = True
                                else:
                                    edit_text = "❌ Не удалось скачать"
                            else:
                                edit_text = "❌ Видео не найдено"
                        else:
                            edit_text = "❌ Проверьте ссылку"
                    except:
                        edit_text = "❌ Ошибка"

    elif cmd == ".weather":
        if not args:
            edit_text = "❌ Укажите город: .weather Москва"
        else:
            try:
                url = f"{WEATHER_API}{urllib.parse.quote(args)}?format=3&lang=ru"
                resp = requests.get(url, timeout=10)
                edit_text = f"🌤 {resp.text.strip()}"
            except:
                edit_text = "❌ Ошибка получения погоды"

    elif cmd == ".translate":
        if not args:
            edit_text = "❌ .translate фраза"
        else:
            try:
                params = {"client": "gtx", "sl": "auto", "tl": "ru", "dt": "t", "q": args}
                resp = requests.get(TRANSLATE_API, params=params, timeout=10)
                result = "".join([s[0] for s in resp.json()[0] if s[0]])
                edit_text = f"🌐 {result}"
            except:
                edit_text = "❌ Ошибка перевода"

    elif cmd == ".calc":
        if not args:
            edit_text = "❌ .calc 2+2*3"
        else:
            try:
                allowed = set("0123456789+-*/().% ")
                if not all(c in allowed for c in args):
                    edit_text = "❌ Только + - * / ( )"
                else:
                    result = eval(args)
                    edit_text = f"🧮 {args} = {result}"
            except:
                edit_text = "❌ Ошибка вычисления"

    elif cmd == ".qr":
        if not args:
            edit_text = "❌ .qr ссылка"
        else:
            try:
                url = f"{QR_API}?size=300x300&data={urllib.parse.quote(args)}"
                edit_photo = url
                edit_caption = "📱 QR-код"
            except:
                edit_text = "❌ Ошибка создания QR-кода"

    elif cmd == ".poll":
        if not args:
            edit_text = "❌ .poll Вопрос? / Да / Нет"
        else:
            parts = args.split("/")
            if len(parts) < 3:
                edit_text = "❌ Вопрос + 2 варианта через /"
            else:
                question = parts[0].strip()
                options = [p.strip() for p in parts[1:] if p.strip()]
                if len(options) > 10:
                    edit_text = "❌ Максимум 10 вариантов"
                else:
                    await msg.delete()
                    await msg.reply_poll(question=question, options=options, is_anonymous=False)
                    return

    elif cmd == ".fact":
        try:
            resp = requests.get(FACT_API, timeout=10)
            data = resp.json()
            fact = data.get("text", "")
            if fact:
                fact_ru = google_translate(fact, source='en', target='ru')
                edit_text = f"💡 {fact_ru}"
            else:
                edit_text = "❌ Не удалось получить факт"
        except:
            edit_text = "❌ Ошибка получения факта"

    elif cmd == ".joke":
        try:
            url = f"{JOKE_API}?lang=ru&blacklistFlags=nsfw,racist,sexist"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get("type") == "twopart":
                edit_text = f"😂 {data.get('setup', '')}\n\n😄 {data.get('delivery', '')}"
            else:
                edit_text = f"😂 {data.get('joke', '')}"
        except:
            edit_text = "❌ Не удалось получить шутку"

    elif cmd == ".quote":
        try:
            resp = requests.get(QUOTE_API, timeout=10)
            data = resp.json()
            quote = data.get("content", "")
            author = data.get("author", "Неизвестный")
            if quote:
                quote_ru = google_translate(quote, source='en', target='ru')
                edit_text = f"📜 {quote_ru}\n\n— {author}"
            else:
                edit_text = "❌ Не удалось получить цитату"
        except:
            edit_text = "❌ Ошибка получения цитаты"

    elif cmd == ".limit":
        user_id_limits = msg.from_user.id if msg.from_user else msg.chat_id
        today = datetime.now().date()
        if user_id_limits in user_limits and user_limits[user_id_limits][0] == today:
            used = user_limits[user_id_limits][1]
            edit_text = f"📊 Сегодня скачано {used}/5, осталось: {5-used}"
        else:
            edit_text = "📊 Сегодня ещё не скачивали. Доступно: 5/5"

    elif cmd == ".troll":
        phrases = random.sample(TROLL_PHRASES, min(5, len(TROLL_PHRASES)))
        edit_text = phrases[0]
        for phrase in phrases[1:]:
            await msg.reply_text(phrase)

    elif cmd == ".a_troll":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение"
        else:
            target = msg.reply_to_message.from_user
            auto_trolls[msg.chat_id] = target.id
            edit_text = f"🤡 Автотроллинг включён на {target.first_name}\n.a_troll_off — выключить"

    elif cmd == ".a_troll_off":
        if msg.chat_id in auto_trolls:
            del auto_trolls[msg.chat_id]
            edit_text = "🔇 Автотроллинг выключен"
        else:
            edit_text = "❌ Автотроллинг не был включён"

    elif cmd == ".voice":
        if not args:
            edit_text = "❌ .voice текст"
        else:
            try:
                tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=gtx&tl=ru&q={urllib.parse.quote(args)}"
                resp = requests.get(tts_url, timeout=15)
                if resp.status_code == 200:
                    edit_voice = resp.content
                    edit_caption = f"🔊 {args[:50]}..."
                    delete_and_send_new = True
                else:
                    edit_text = "❌ Не удалось озвучить"
            except:
                edit_text = "❌ Ошибка озвучки"

    elif cmd == ".search":
        if not args:
            edit_text = "❌ .search запрос"
        else:
            edit_text = f"🔍 https://www.google.com/search?q={urllib.parse.quote(args)}"

    elif cmd == ".cat":
        try:
            resp = requests.get(CAT_API, timeout=10)
            data = resp.json()
            if data and len(data) > 0:
                edit_photo = data[0]["url"]
                edit_caption = "🐱 Котик!"
            else:
                edit_text = "❌ Не удалось найти котика"
        except:
            edit_text = "❌ Не удалось найти котика"

    elif cmd == ".dog":
        try:
            resp = requests.get(DOG_API, timeout=10)
            data = resp.json()
            if data and len(data) > 0:
                edit_photo = data[0]["url"]
                edit_caption = "🐶 Собачка!"
            else:
                edit_text = "❌ Не удалось найти собачку"
        except:
            edit_text = "❌ Не удалось найти собачку"

    elif cmd == ".time":
        zone = args if args else "Europe/Moscow"
        try:
            resp = requests.get(f"{TIME_API}/{urllib.parse.quote(zone)}", timeout=5)
            data = resp.json()
            if 'datetime' in data:
                dt = data['datetime']
                edit_text = f"🕒 {data['timezone']}: {dt[:10]} {dt[11:19]}"
            else:
                edit_text = "❌ Не удалось получить время"
        except:
            edit_text = "❌ Не удалось получить время"

    elif cmd == ".wiki":
        if not args:
            edit_text = "❌ .wiki запрос"
        else:
            try:
                headers = {"User-Agent": "BoBmod/1.0"}
                url = f"{WIKI_API}{urllib.parse.quote(args)}"
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()
                if data.get("extract"):
                    edit_text = f"📚 {data['title']}\n\n{data['extract'][:1000]}...\n\n{data.get('content_urls', {}).get('desktop', {}).get('page', '')}"
                else:
                    edit_text = "❌ Статья не найдена"
            except:
                edit_text = "❌ Статья не найдена"

    elif cmd == ".dice":
        value = random.randint(1, 6)
        edit_text = f"🎲 Выпало: {value}"

    elif cmd == ".coin":
        result = random.choice(["Орёл", "Решка"])
        edit_text = f"🪙 Результат: {result}"

    elif cmd == ".password":
        length = 16
        if args.isdigit():
            length = min(int(args), 64)
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        edit_text = f"🔑 Пароль ({length} символов): <code>{password}</code>"

    elif cmd == ".nick":
        adjectives = ["Бешеный", "Хитрый", "Весёлый", "Ленивый", "Быстрый", "Храбрый"]
        nouns = ["Кот", "Пёс", "Лис", "Панда", "Тигр"]
        nick = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10,99)}"
        edit_text = f"📛 Ваш ник: {nick}"

    elif cmd == ".mock":
        if not args:
            edit_text = "❌ .mock текст"
        else:
            mocked = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(args))
            edit_text = mocked

    elif cmd == ".reverse":
        if not args:
            edit_text = "❌ .reverse текст"
        else:
            edit_text = args[::-1]

    elif cmd == ".vaporwave":
        if not args:
            edit_text = "❌ .vaporwave текст"
        else:
            vapor = " ".join(args.upper())
            edit_text = vapor

    elif cmd == ".bold":
        if not args:
            edit_text = "❌ .bold текст"
        else:
            bold_map = str.maketrans(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
            )
            edit_text = args.translate(bold_map)

    elif cmd == ".italic":
        if not args:
            edit_text = "❌ .italic текст"
        else:
            italic_map = str.maketrans(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"
            )
            edit_text = args.translate(italic_map)

    elif cmd == ".hug":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение"
        else:
            user1 = msg.from_user.first_name
            user2 = msg.reply_to_message.from_user.first_name
            edit_text = f"🤗 {user1} обнял(а) {user2}"

    elif cmd == ".slap":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение"
        else:
            user1 = msg.from_user.first_name
            user2 = msg.reply_to_message.from_user.first_name
            edit_text = f"👋 {user1} дал(а) леща {user2}"

    elif cmd == ".pat":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение"
        else:
            user1 = msg.from_user.first_name
            user2 = msg.reply_to_message.from_user.first_name
            edit_text = f"🫳 {user1} погладил(а) {user2}"

    elif cmd == ".kill":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение"
        else:
            user1 = msg.from_user.first_name
            user2 = msg.reply_to_message.from_user.first_name
            edit_text = f"💀 {user1} убил(а) {user2}"

    elif cmd == ".photo":
        if not args:
            edit_text = "❌ .photo запрос"
        else:
            try:
                photos = search_pexels_photos(args, 3)
                if photos:
                    await msg.delete()
                    for i, url in enumerate(photos):
                        caption = f"📷 {args}\n🔍 Результат {i+1}/{len(photos)}" if i == 0 else ""
                        await msg.reply_photo(photo=url, caption=caption)
                    return
                else:
                    edit_text = "❌ Фото не найдены. Попробуйте другой запрос."
            except Exception as e:
                print(f"Photo error: {e}")
                edit_text = "❌ Фото не найдены."

    elif cmd == ".base64":
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            edit_text = "❌ Используйте: .base64 enc <текст> или .base64 dec <текст>"
        else:
            action = parts[0].lower()
            text = parts[1]
            try:
                if action == "enc":
                    result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
                    edit_text = f"🔒 Закодировано:\n<code>{result}</code>"
                elif action == "dec":
                    result = base64.b64decode(text.encode('utf-8')).decode('utf-8')
                    edit_text = f"🔓 Раскодировано:\n<code>{result}</code>"
                else:
                    edit_text = "❌ Неизвестное действие. Используйте enc или dec."
            except Exception as e:
                edit_text = f"❌ Ошибка Base64: {e}"

    elif cmd == ".rps":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение соперника"
        else:
            opponent = msg.reply_to_message.from_user
            active_games[msg.chat_id] = {
                "game": "rps",
                "moves": {},
                "players": [msg.from_user.id, opponent.id]
            }
            keyboard = [
                [InlineKeyboardButton("🪨 Камень", callback_data="rps_r"),
                 InlineKeyboardButton("📄 Ножницы", callback_data="rps_p"),
                 InlineKeyboardButton("✂️ Бумага", callback_data="rps_s")]
            ]
            await msg.delete()
            await msg.reply_text("Выберите:", reply_markup=InlineKeyboardMarkup(keyboard))
            return

    elif cmd == ".ttt":
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            edit_text = "❌ Ответьте на сообщение соперника"
        else:
            opponent = msg.reply_to_message.from_user
            board = [[" " for _ in range(3)] for _ in range(3)]
            active_games[msg.chat_id] = {
                "game": "ttt",
                "board": board,
                "players": {msg.from_user.id: "X", opponent.id: "O"},
                "turn": msg.from_user.id
            }
            await msg.delete()
            await msg.reply_text("Крестики-нолики", reply_markup=build_ttt_keyboard(board))
            return

    # Применяем изменения
    if delete_and_send_new:
        try:
            await msg.delete()
        except:
            pass
        if edit_video:
            await msg.reply_video(video=edit_video, caption=edit_caption or "", supports_streaming=True)
        elif edit_voice:
            await msg.reply_voice(voice=edit_voice, caption=edit_caption or "")
        elif edit_photo:
            await msg.reply_photo(photo=edit_photo, caption=edit_caption or "")
    elif edit_photo:
        try:
            await msg.edit_text(edit_caption or "📷", reply_markup=None)
            await msg.reply_photo(photo=edit_photo, caption=edit_caption or "")
        except:
            await msg.reply_photo(photo=edit_photo, caption=edit_caption or "")
    elif edit_text:
        try:
            await msg.edit_text(edit_text)
        except Exception as e:
            print(f"Edit error: {e}")
            try:
                await msg.reply_text(edit_text)
            except:
                pass

async def deleted_messages_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.deleted_messages:
        return
    for deleted_msg in update.deleted_messages:
        chat_id = deleted_msg.chat.id
        owner_id = business_owners.get(chat_id)
        if owner_id is None:
            continue
        for msg_id in deleted_msg.message_ids:
            if chat_id in message_cache and msg_id in message_cache[chat_id]:
                from_user, text = message_cache[chat_id][msg_id]
                user_mention = f"@{from_user.username}" if from_user and from_user.username else (from_user.first_name if from_user else "Неизвестный")
                notify_text = f"🗑 <b>{user_mention}</b> удалил сообщение:\n{text}"
                await context.bot.send_message(owner_id, notify_text, parse_mode="HTML")
                del message_cache[chat_id][msg_id]

async def all_updates_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(update, 'deleted_messages') and update.deleted_messages:
        await deleted_messages_handler(update, context)

async def update_nicknames(context: ContextTypes.DEFAULT_TYPE):
    for user_id_str, settings in list(user_settings.items()):
        if not settings.get("time_in_nick"):
            continue
        user_id = int(user_id_str)
        biz_conn_id = business_connections.get(user_id)
        if not biz_conn_id:
            continue
        tz_key = settings.get("timezone", "Europe/Moscow")
        try:
            resp = requests.get(f"http://worldtimeapi.org/api/timezone/{tz_key}", timeout=3)
            data = resp.json()
            if 'datetime' in data:
                dt = data['datetime']
                time_str = f"{dt[11:16]}"
                base_name = settings.get("base_name", "User")
                new_name = f"{base_name} ({time_str})"
                await context.bot.set_business_account_name(
                    business_connection_id=biz_conn_id,
                    first_name=new_name
                )
        except Exception as e:
            print(f"Ошибка обновления ника: {e}")

def main():
    import os
    # Очищаем переменные SOCKS/прокси, чтобы httpx не падал
    for var in ["HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "SOCKS_PROXY",
                "https_proxy", "http_proxy", "all_proxy", "socks_proxy"]:
        os.environ.pop(var, None)
    os.environ["NO_PROXY"] = "*"

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(BusinessConnectionHandler(on_business_connection))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(TypeHandler(Update, all_updates_handler))
    app.add_handler(CallbackQueryHandler(handle_callback))

    try:
        job_queue = app.job_queue
        if job_queue:
            job_queue.run_repeating(update_nicknames, interval=60, first=10)
    except Exception as e:
        print(f"JobQueue не настроен: {e}")

    print("🤖 BoBmod v3.5 (без AI) запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
