import os
import re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8030110367:AAErMXwJnkXPhTMLuojFEHq39Oi_odgHpUE"
bot = telebot.TeleBot(BOT_TOKEN)

NUMBERS_FILE = "used_numbers.txt"
if os.path.exists(NUMBERS_FILE):
    with open(NUMBERS_FILE, "r", encoding="utf-8") as f:
        used_numbers = set(line.strip() for line in f if line.strip())
else:
    used_numbers = set()

user_data = {}

# ————————————————————————— КЛАВИАТУРЫ ——————————————————————————

def back_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("↩ Назад", callback_data="to_menu"),
        InlineKeyboardButton("🏠 В меню", callback_data="to_menu"),
    )
    return kb

def inline_main_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("🏠 Главная", url="https://лд.рф"),
        InlineKeyboardButton("📋 Вакансии", callback_data="MENU_VACANCIES"),
        InlineKeyboardButton("🏭 О предприятии", callback_data="MENU_ABOUT"),
        InlineKeyboardButton("📦 Каталог", url="https://лд.рф/catalog/"),
        InlineKeyboardButton("📇 Контакты", callback_data="MENU_CONTACTS"),
        InlineKeyboardButton("📲 Заказать звонок", callback_data="MENU_CALL"),
    )
    return kb

def send_main_menu(chat_id):
    bot.send_message(chat_id, "Главное меню:", reply_markup=inline_main_keyboard())

# ———————————————————— ДАННЫЕ —————————————————————

PREP_LINK = "Материал для подготовки здесь!\nhttps://ld-center.getcourse.ru/start\n\n"

exam_table = {
    "prod_zag_1": "Полный экзамен включает: чтение технических чертежей, основы метрологии, правила охраны труда и должностную инструкцию.",
    "prod_zag_2": "Неполный экзамен + измерительный инструмент: вопросы по инструкции, охране труда и практическое владение линейкой и штангенциркулем.",
    "prod_zag_3": "Неполный экзамен: вопросы по должностной инструкции и правилам охраны труда.",

    "prod_rem_1": "Полный экзамен: чтение чертежей, нормативные документы, технологические процессы, охрана труда.",
    "prod_rem_2": "Неполный экзамен: вопросы по инструкции и охране труда (для грузчика).",
    "prod_rem_3": "Неполный экзамен + инструмент: теория станков и практическая проверка навыков.",
    "prod_rem_4": "Неполный экзамен: вопросы по охране труда и инструкции (для оператора ленточнопильного станка).",
    "prod_rem_5": "Неполный экзамен: требования к нагреву печей и охране труда (для термиста).",
    "prod_rem_6": "Неполный экзамен: вопросы по инструкции и охране труда (для грузчика).",

    "prod_red_1": "Полный экзамен: чтение чертежей, основы зубофрезерования, метрология и охрана труда.",
    "prod_red_2": "Неполный экзамен + сварка: тест по сварочным технологиям и охране труда.",
    "prod_red_3": "Неполный экзамен: вопросы по инструкции и охране труда.",
    "prod_red_4": "Неполный экзамен + сварка: проверка практических навыков и техники безопасности.",

    "prod_flan_1": "Полный экзамен: чтение чертежей фланцев, основы гидравлики, метрология и охрана труда.",
    "prod_flan_2": "Неполный экзамен + инструмент: владение штангенциркулем и вопросы по охране труда.",
    "prod_flan_3": "Неполный экзамен + сварка: теория сварки фланцев и техника безопасности.",
    "prod_flan_4": "Неполный экзамен: вопросы по инструкции и охране труда.",
    "prod_flan_5": "Неполный экзамен + сварка: проверка навыков электросварки и охраны труда.",
    "prod_flan_6": "Неполный экзамен: вопросы по инструкции и охране труда (для галтовщика).",

    "prod_kran_1": "Полный экзамен: чтение схем кранов, основы механики, метрология и охрана труда.",
    "prod_kran_2": "Неполный экзамен + практика работы ленточнопильным станком и ОТ.",
    "prod_kran_3": "Неполный экзамен + техдокументация: знания ЧПУ-станков и охрана труда.",
    "prod_kran_4": "Неполный экзамен: вопросы по сварке и охране труда.",
    "prod_kran_5": "Неполный экзамен: вопросы по полировке и охране труда.",
    "prod_kran_6": "Неполный экзамен: вопросы по инструкции и охране труда (для грузчика).",

    "prod_polu_1": "Полный экзамен: чертежи, основы резки, метрология и охрана труда.",
    "prod_polu_2": "Неполный экзамен + сварка: проверка сварочных навыков и охраны труда.",
    "prod_polu_3": "Неполный экзамен + техдокументация: вопросы по полировке и охране труда.",
    "prod_polu_4": "Неполный экзамен: вопросы по инструкции и охране труда.",
    "prod_polu_5": "Неполный экзамен: вопросы по полировке и охране труда.",
    "prod_polu_6": "Неполный экзамен: требования к термисту и охране труда.",
    "prod_polu_7": "Неполный экзамен: вопросы по СОЖ, ГСМ и охране труда.",

    "prod_sbor_1": "Полный экзамен: сборка по чертежам, метрология, охрана труда и инструкция.",
    "prod_sbor_2": "Неполный экзамен: вопросы по инструкции и охране труда.",
    "prod_sbor_3": "Неполный экзамен + сварка: проверка сварочных навыков и охраны труда.",
    "prod_sbor_4": "Неполный экзамен: вопросы по сборке и охране труда.",

    "eng_1_1": "Полный экзамен: чтение сложных чертежей, разработка техпроцессов, охрана труда и инструкция.",
    "eng_1_2": "Неполный экзамен + сварка: теория сварочного производства и охрана труда.",

    "eng_kach_1": "Полный экзамен: основы метрологии, методики контроля, охрана труда и инструкция.",
    "eng_kach_2": "Неполный экзамен: стандарты контроля качества и охрана труда.",

    "eng_otk_z_1": "Полный экзамен: чертежи заготовок, макеты, охрана труда и инструкция.",
    "eng_otk_z_2": "Неполный экзамен: вопросы по охране труда и инструкции.",

    "eng_otk_s_1": "Полный экзамен: чертежи сборки, сварка, охрана труда и инструкция.",
    "eng_otk_s_2": "Неполный экзамен: вопросы по охране труда и инструкции.",

    "eng_lab_1": "Полный экзамен: методики НК, интерпретация данных, охрана труда и инструкция.",
    "eng_lab_2": "Неполный экзамен: требования к испытательным стендам и охрана труда.",

    "eng_serv_1": "Полный экзамен: документация по сервису, охрана труда и инструкция.",
}

sections = [
    ("prod_zag", "📁 Заготовительный цех"),
    ("prod_rem", "🔧 Ремонтно-инструментальный цех"),
    ("prod_red", "⚙️ Участок производства редукторов"),
    ("prod_flan", "🛠 Фланцевый цех"),
    ("prod_kran", "🏗 Цех больших кранов"),
    ("prod_polu", "🧱 Цех полуфабрикатов"),
    ("prod_sbor", "🔩 Цех серийной сборки"),
    ("eng_main", "✏️ Инженерно-технические должности"),
    ("eng_kach", "🧮 Служба качества"),
    ("eng_otk_z", "🔎 ОТК (заготовка)"),
    ("eng_otk_s", "🛠 ОТК (сборка и сварка)"),
    ("eng_lab", "📡 Лаборатория неразрушающего контроля"),
    ("eng_serv", "🧰 Сервисная служба"),
]

section_map = {
    "prod_zag": [
        ("1) Мастер, токарь", "prod_zag_1"),
        ("2) Бригадир-оператор ленточнопильного станка", "prod_zag_2"),
        ("3) Галтовщик, грузчик", "prod_zag_3"),
    ],
    "prod_rem": [
        ("1) Мастер, инженер-экономист, инженер-технолог, инженер по качеству", "prod_rem_1"),
        ("2) Грузчик", "prod_rem_2"),
        ("3) Наладчик токарной группы, наладчик ЧПУ, оператор ЧПУ", "prod_rem_3"),
        ("4) Оператор ленточнопильного станка", "prod_rem_4"),
        ("5) Термист нагревательных печей, слесарь-инструментальщик", "prod_rem_5"),
        ("6) Грузчик", "prod_rem_6"),
    ],
    "prod_red": [
        ("1) Мастер, маляр, оператор зубофрезерного станка, токарь, оператор ЧПУ", "prod_red_1"),
        ("2) Наладчик ЧПУ, слесарь механо-сборочных работ", "prod_red_2"),
        ("3) Термист нагревательных печей", "prod_red_3"),
        ("4) Электросварщик на автоматических и п/автоматических машинах", "prod_red_4"),
    ],
    "prod_flan": [
        ("1) Мастер, оператор ЧПУ, токарь, сверловщик", "prod_flan_1"),
        ("2) Наладчик токарных автоматов, наладчик холодноштамповочного оборудования", "prod_flan_2"),
        ("3) Наладчик шестишпиндельного автомата, слесарь-инструментальщик", "prod_flan_3"),
        ("4) Оператор ленточнопильного станка", "prod_flan_4"),
        ("5) Электросварщик на автоматических и п/автоматических машинах", "prod_flan_5"),
        ("6) Галтовщик, грузчик, зенковщик", "prod_flan_6"),
    ],
    "prod_kran": [
        ("1) Мастер, маляр, наладчик холодноштамповочного оборудования", "prod_kran_1"),
        ("2) Оператор ленточнопильного станка, оператор машины термической резки", "prod_kran_2"),
        ("3) Оператор ЧПУ, робототехник, сверловщик, токарь, фрезеровщик", "prod_kran_3"),
        ("4) Электросварщик на автоматических и п/автоматических машинах", "prod_kran_4"),
        ("5) Полировщик", "prod_kran_5"),
        ("6) Грузчик, оператор дробеструйной установки, разнорабочий, упаковщик", "prod_kran_6"),
    ],
    "prod_polu": [
        ("1) Мастер, наладчик мех. ножниц, оператор ЧПУ, резчик металла, строгальщик-долбежник", "prod_polu_1"),
        ("2) Электросварщик на автоматических и п/автоматических машинах", "prod_polu_2"),
        ("3) Полировщик, оператор холодноштамповочного оборудования, термист печей", "prod_polu_3"),
        ("4) Грузчик, оператор термодиффузионной установки, специалист по СОЖ и ГСМ", "prod_polu_4"),
        ("5) Полировщик, оператор холодноштамповочного оборудования", "prod_polu_5"),
        ("6) Термист нагревательных печей", "prod_polu_6"),
        ("7) Грузчик, оператор термодиффузионной установки, специалист по СОЖ и ГСМ", "prod_polu_7"),
    ],
    "prod_sbor": [
        ("1) Мастер, маляр, наладчик ЧПУ, оператор ЧПУ, токарь", "prod_sbor_1"),
        ("2) Электросварщик на автоматических и п/автоматических машинах", "prod_sbor_2"),
        ("3) Грузчик, оператор дробеструйной установки, слесарь механо-сборочных работ, упаковщик", "prod_sbor_3"),
        ("4) Грузчик, оператор дробеструйной установки, слесарь механо-сборочных работ, упаковщик", "prod_sbor_4"),
    ],
    "eng_main": [
        ("1) Инженер-технолог, инженер-электроник, конструктор, технол-конструктор, технолог металлообработки", "eng_1_1"),
        ("2) Технолог сварочного производства", "eng_1_2"),
    ],
    "eng_kach": [
        ("1) Метролог", "eng_kach_1"),
        ("2) Инженер по качеству, инженер по входному контролю", "eng_kach_2"),
    ],
    "eng_otk_z": [
        ("1) Контролер, старший контролер", "eng_otk_z_1"),
        ("2) Мастер", "eng_otk_z_2"),
    ],
    "eng_otk_s": [
        ("1) Старший контролер, контролер, оператор лазерных технологий", "eng_otk_s_1"),
        ("2) Мастер", "eng_otk_s_2"),
    ],
    "eng_lab": [
        ("1) Дефектоскопист-рентгенолог, дефектоскопист", "eng_lab_1"),
        ("2) Оператор испытательного стенда, старший оператор", "eng_lab_2"),
    ],
    "eng_serv": [
        ("1) Инженер", "eng_serv_1"),
    ],
}

# ———————————————————— ХЕНДЛЕРЫ —————————————————————

@bot.message_handler(commands=['start'])
def cmd_start(m):
    send_main_menu(m.chat.id)

@bot.callback_query_handler(func=lambda c: c.data == "to_menu")
def cb_to_menu(c):
    user_data.pop(c.message.chat.id, None)
    send_main_menu(c.message.chat.id)
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data == "MENU_VACANCIES")
def cb_menu_vacancies(c):
    kb = InlineKeyboardMarkup(row_width=1)
    for idx, (key, title) in enumerate(sections, start=1):
        kb.add(InlineKeyboardButton(f"{idx}. {title}", callback_data=key))
    kb.add(InlineKeyboardButton("🏠 В меню", callback_data="to_menu"))
    bot.edit_message_text("Выберите подразделение:", c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data == "MENU_ABOUT")
def cb_menu_about(c):
    about = (
        "ЧелябинскСпецГражданСтрой (ЧСГС) под брендом LD работает с 2003 года.\n\n"
        "🏭 Ведущий уральский производитель стальных шаровых кранов\n"
        "📍 5 площадок, более 2800 сотрудников\n"
        "⚙️ Полный цикл: проектирование → производство → контроль качества → логистика\n"
        "✅ Гарантия 10 лет и сервис 24/7\n"
        "🌍 Партнёры: Газпром и крупные теплоэнергосетевые компании\n\n"
        "Миссия: надёжная трубопроводная арматура для промышленности и ЖКХ."
    )
    bot.edit_message_text(about, c.message.chat.id, c.message.message_id, reply_markup=back_keyboard())
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data == "MENU_CONTACTS")
def cb_menu_contacts(c):
    contact = (
        "📞 Телефон/факс:\n"
        "+7 (351) 730-47-47\n"
        "+7 (351) 796-30-85\n\n"
        "✉️ Email: office@chsgs.ru\n"
        "🌐 Сайт: www.chsgs.ru"
    )
    bot.edit_message_text(contact, c.message.chat.id, c.message.message_id, reply_markup=back_keyboard())
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data == "MENU_CALL")
def cb_menu_call(c):
    user_data[c.message.chat.id] = {"waiting": "name"}
    bot.edit_message_text("Введите ваше имя (только буквы):", c.message.chat.id, c.message.message_id, reply_markup=back_keyboard())
    bot.answer_callback_query(c.id)
    bot.register_next_step_handler_by_chat_id(c.message.chat.id, process_name)

def process_name(m):
    state = user_data.get(m.chat.id)
    if not state or state.get("waiting") != "name":
        return
    txt = m.text.strip()
    if txt in ("↩ Назад", "🏠 В меню"):
        user_data.pop(m.chat.id, None)
        send_main_menu(m.chat.id)
        return
    if not re.fullmatch(r"[А-Яа-яЁё ]{2,}", txt):
        bot.send_message(m.chat.id, "❗ Имя должно содержать только русские буквы.", reply_markup=back_keyboard())
        bot.register_next_step_handler(m, process_name)
        return
    user_data[m.chat.id] = {"name": txt, "waiting": "phone"}
    bot.send_message(
        m.chat.id,
        "Введите номер телефона +7 (***) ***-**-**\n",
        reply_markup=back_keyboard()
    )
    bot.register_next_step_handler(m, process_phone)

def process_phone(m):
    state = user_data.get(m.chat.id)
    if not state or state.get("waiting") != "phone":
        return
    txt = m.text.strip()
    if txt in ("↩ Назад", "🏠 В меню"):
        user_data.pop(m.chat.id, None)
        send_main_menu(m.chat.id)
        return
    if not re.fullmatch(r"\+7\d{10}", txt):
        bot.send_message(m.chat.id, "❗ Формат: +7********** (12 символов).", reply_markup=back_keyboard())
        bot.register_next_step_handler(m, process_phone)
        return
    if txt in used_numbers:
        bot.send_message(m.chat.id, "⚠️ Этот номер уже введён. Введите другой:", reply_markup=back_keyboard())
        bot.register_next_step_handler(m, process_phone)
        return
    used_numbers.add(txt)
    with open(NUMBERS_FILE, "a", encoding="utf-8") as f:
        f.write(txt + "\n")
    name = state["name"]
    user_data.pop(m.chat.id, None)
    bot.send_message(
        m.chat.id,
        f"✅ Заявка принята!\nИмя: {name}\nТелефон: {txt}",
        reply_markup=inline_main_keyboard()
    )

@bot.callback_query_handler(func=lambda c: c.data in dict(sections))
def cb_show_positions(c):
    kb = InlineKeyboardMarkup(row_width=1)
    for label, cb_data in section_map[c.data]:
        kb.add(InlineKeyboardButton(label, callback_data=cb_data))
    kb.add(InlineKeyboardButton("↩ Назад", callback_data="MENU_VACANCIES"))
    kb.add(InlineKeyboardButton("🏠 В меню", callback_data="to_menu"))
    bot.edit_message_text("Выберите должность:", c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data in exam_table)
def cb_send_exam(c):
    bot.send_message(
        c.message.chat.id,
        PREP_LINK + exam_table[c.data],
        reply_markup=inline_main_keyboard()
    )
    bot.answer_callback_query(c.id)

bot.polling(none_stop=True)
