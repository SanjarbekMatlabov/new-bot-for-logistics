import telebot
import pandas as pd
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
from uuid import uuid4

TOKEN = '6343017062:AAHUp8ujNzR0XlS8RubOTQKDCN_MtWX5T8U'
bot = telebot.TeleBot(TOKEN)

EXCEL_FILE = 'products.xlsx'

SUCCESS_STICKER = 'CAACAgIAAxkBAAIBG2YJ5qGf...' 
ERROR_STICKER = 'CAACAgIAAxkBAAIBH2YJ5qH...'  

# Excel faylni o'qish
def read_excel():
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            print("Ustun nomlari:", df.columns.tolist())  # Debugging uchun
            print("Trek kodlari (birinchi 5 ta):", df['Shipment Tracking Code'].head().tolist())  # Trek kodlarini ko'rish
            return df
        else:
            print(f"{EXCEL_FILE} fayli topilmadi.")
            return pd.DataFrame(columns=['Shipment Tracking Code', 'Shipping Name', 'Package Number', 'Weight/KG', 'Quantity', 'Flight', 'Customer code'])
    except Exception as e:
        print(f"Excel faylni o'qishda xatolik: {e}")
        return pd.DataFrame(columns=['Shipment Tracking Code', 'Shipping Name', 'Package Number', 'Weight/KG', 'Quantity', 'Flight', 'Customer code'])

# Ma'lumotlarni qidirish
def search_product(code):
    df = read_excel()
    try:
        # Trek kodini tozalash va kichik harfga o'tkazish
        code = str(code).strip().lower()
    except ValueError:
        pass
    if 'Shipment Tracking Code' in df.columns:
        # Exceldagi trek kodlarini ham kichik harfga o'tkazib solishtirish
        df['Shipment Tracking Code'] = df['Shipment Tracking Code'].astype(str).str.strip().str.lower()
        result = df[df['Shipment Tracking Code'] == code]
        if not result.empty:
            return result[['Shipping Name', 'Package Number', 'Weight/KG', 'Quantity', 'Flight', 'Customer code']].to_dict('records')
        return None
    else:
        print("Xatolik: 'Shipment Tracking Code' ustuni topilmadi.")
        return None

# Asosiy menyuni yaratish
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Yukni qidirish 📦"))
    return markup

# Start komandasi
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "Assalomu alaykum! 🎉\n"
        "Men yuk ma'lumotlarini qidiruvchi botman.\n"
        "Yukingiz haqida ma'lumot olish uchun 'Yukni qidirish 📦' tugmasini bosing!"
    )
    bot.reply_to(message, welcome_msg, reply_markup=main_menu())

# Xabar ishlovchisi
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Yukni qidirish 📦":
        bot.reply_to(message, "Trek kodini kiriting (masalan, JTS341590726333):")
        bot.register_next_step_handler(message, search_by_code)
    else:
        bot.reply_to(message, "Iltimos, 'Yukni qidirish 📦' tugmasini bosing:", reply_markup=main_menu())

# Yuk raqami bo'yicha qidirish
def search_by_code(message):
    code = message.text.strip()
    results = search_product(code)
    
    if results:
        for item in results:
            response = (
                "✅ Yuk topildi!\n\n"
                f"📦 Mahsulot: {item['Shipping Name']}\n"
                f"📏 Paket raqami: {item['Package Number']}\n"
                f"⚖️ Vazn: {item['Weight/KG']} kg\n"
                f"🔢 Miqdor: {item['Quantity']}\n"
                f"✈️ Parvoz: {item['Flight']}\n"
                f"👤 Mijoz kodi: {item['Customer code']}"
            )
            bot.reply_to(message, response)
            bot.send_sticker(message.chat.id, SUCCESS_STICKER)  # Muvaffaqiyat stikeri
    else:
        bot.reply_to(message, f"❌ {code} trek kodiga mos yuk topilmadi.\nIltimos, trek kodini to'g'ri kiritganingizga ishonch hosil qiling (masalan, JTS341590726333).")
        bot.send_sticker(message.chat.id, ERROR_STICKER)  # Xatolik stikeri
    
    bot.reply_to(message, "Yana qidirish uchun 'Yukni qidirish 📦' tugmasini bosing:", reply_markup=main_menu())

# Botni ishga tushirish
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        import time
        time.sleep(5)
        bot.polling(none_stop=True)