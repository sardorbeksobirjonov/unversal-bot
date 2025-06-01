import telebot
from telebot import types

BOT_TOKEN = "8029301761:AAH0FPgTg-S0zI4qji_xqFu_y7U4lnC878w"
ADMIN_IDS = [7700441769,7670972092]

bot = telebot.TeleBot(BOT_TOKEN)

user_orders = {}
menu_items = [
    "YFC\nYangiyol Fried Chicken 🍗",
    "Qanot\n1 kg • 75.000\n0,5 kg • 40.000\n1 portsa • 25.000",
    "Lagmon\n1 kg • 80.000\n0,5 kg • 40.000\n1 portsa • 28.000"
]

ADMIN_PASSWORD = "adminparol"

def start_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Menu", "Buyurtma berish", "Admin")
    return keyboard

def contact_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)
    keyboard.add(button)
    return keyboard

def admin_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Menu o'zgartirish", "Menu o'chirish", "Reklama tarqatish")
    keyboard.row("Chiqish")
    return keyboard

def menu_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for idx, item in enumerate(menu_items):
        # Har bir menyu elementining birinchi qatordagi nomini tugma sifatida olamiz
        name = item.split("\n")[0]
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=f"menu_{idx}"))
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    start_text = (
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "🍟 Bu bot orqali YFC menyusini ko'rishingiz yoki buyurtma berishingiz mumkin.\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    bot.send_message(message.chat.id, start_text, parse_mode='HTML', reply_markup=start_keyboard())

@bot.message_handler(func=lambda m: m.text == "Menu")
def show_menu(message):
    menu_text = "<b>📋 YFC Menyu:</b>\n\n"
    for item in menu_items:
        menu_text += f"{item}\n\n"
    bot.send_message(message.chat.id, menu_text, parse_mode='HTML', reply_markup=menu_inline_keyboard())

@bot.message_handler(func=lambda m: m.text == "Buyurtma berish")
def start_order(message):
    bot.send_message(message.chat.id, "Kerakli buyurtma nomini yozing:", reply_markup=types.ReplyKeyboardRemove())
    user_orders[message.chat.id] = {"order": None, "phone": None}
    bot.register_next_step_handler(message, process_order_name)

def process_order_name(message):
    user_orders[message.chat.id]["order"] = message.text
    bot.send_message(message.chat.id, "Telefon raqamingizni yuboring:", reply_markup=contact_keyboard())
    bot.register_next_step_handler(message, process_contact)

def process_contact(message):
    if message.contact is None or message.contact.user_id != message.chat.id:
        bot.send_message(message.chat.id, "Iltimos, o'zingizning telefon raqamingizni yuboring.", reply_markup=contact_keyboard())
        bot.register_next_step_handler(message, process_contact)
        return
    user_orders[message.chat.id]["phone"] = message.contact.phone_number

    username = message.from_user.username or "No username"
    order = user_orders[message.chat.id]["order"]
    phone = user_orders[message.chat.id]["phone"]

    admin_msg = (
        f"🆕 Yangi buyurtma!\n\n"
        f"👤 Foydalanuvchi: @{username}\n"
        f"🆔 ID: {message.chat.id}\n"
        f"📞 Telefon: {phone}\n"
        f"🍗 Buyurtma: {order}"
    )
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, admin_msg)

    user_msg = (
        "✅ Buyurtmangiz qabul qilindi!\n"
        "Biz tez orada siz bilan bog'lanamiz.\n\n"
        "📞 Admin bilan bog'lanish:\n"
        "👤 @junior_developmentt\n"
        "👤 @itssasilbee\n"
        "Rasmiy Yangiyol Chicken 🐔\n"
        "📱 +998 97 609 41 02"
    )
    bot.send_message(message.chat.id, user_msg, reply_markup=start_keyboard())

@bot.message_handler(func=lambda m: m.text == "Admin")
def ask_admin_password(message):
    bot.send_message(message.chat.id, "Iltimos, admin parolini kiriting:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_admin_password)

def check_admin_password(message):
    if message.text == ADMIN_PASSWORD and message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Admin panelga xush kelibsiz!", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "Parol noto‘g‘ri yoki siz admin emassiz.", reply_markup=start_keyboard())

@bot.message_handler(func=lambda m: m.text in ["Menu o'zgartirish", "Menu o'chirish", "Reklama tarqatish", "Chiqish"])
def admin_panel_actions(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "Siz admin emassiz!", reply_markup=start_keyboard())
        return

    if message.text == "Menu o'zgartirish":
        bot.send_message(message.chat.id, "Iltimos, yangi menyu elementini yozing:")
        bot.register_next_step_handler(message, add_menu_item)

    elif message.text == "Menu o'chirish":
        if not menu_items:
            bot.send_message(message.chat.id, "Menyu bo‘sh.", reply_markup=admin_keyboard())
            return
        bot.send_message(message.chat.id, "O‘chirmoqchi bo‘lgan menyu elementini yozing:")
        bot.register_next_step_handler(message, delete_menu_item)

    elif message.text == "Reklama tarqatish":
        bot.send_message(message.chat.id, "Reklama matnini yozing:")
        bot.register_next_step_handler(message, send_advertisement)

    elif message.text == "Chiqish":
        bot.send_message(message.chat.id, "Admin paneldan chiqdingiz.", reply_markup=start_keyboard())

def add_menu_item(message):
    menu_items.append(message.text)
    bot.send_message(message.chat.id, f"'{message.text}' menyuga qo‘shildi.", reply_markup=admin_keyboard())

def delete_menu_item(message):
    try:
        menu_items.remove(message.text)
        bot.send_message(message.chat.id, f"'{message.text}' menyudan o‘chirildi.", reply_markup=admin_keyboard())
    except ValueError:
        bot.send_message(message.chat.id, "Bunday menyu elementi topilmadi.", reply_markup=admin_keyboard())

def send_advertisement(message):
    ad_text = message.text
    for user_id in user_orders.keys():
        try:
            bot.send_message(user_id, f"📢 Reklama:\n\n{ad_text}")
        except Exception:
            pass
    bot.send_message(message.chat.id, "Reklama barcha foydalanuvchilarga yuborildi.", reply_markup=admin_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def menu_button_click(call):
    idx = int(call.data.split("_")[1])
    if 0 <= idx < len(menu_items):
        bot.answer_callback_query(call.id)
        bot.send_message(call.from_user.id, f"📋 Menyu elementi:\n\n{menu_items[idx]}", reply_markup=start_keyboard())
    else:
        bot.answer_callback_query(call.id, text="Noto'g'ri menyu elementi!")

bot.infinity_polling()
