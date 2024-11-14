from telegram import Update, ReplyKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import sqlite3
import requests
import jdatetime
import logging
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('BOT_TOKEN')

logging.basicConfig(filename='log.log', filemode='a', level=logging.INFO, format='%(asctime)s-%(filename)s-%(message)s')

# مراحل برای ConversationHandler
FIRST = range(1)

# ایجاد دیتابیس
def create_database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        username TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        client_name TEXT,
        FOREIGN KEY(chat_id) REFERENCES users(chat_id)
    )''')
    
    connection.commit()
    connection.close()

# پیام‌ها
messages = {
    'msg-main-menu': 'منوی اصلی',
    'msg-help': 'سلام به کانفیگ چکر خوش اومدید...',
    'btn-check': 'بررسی کانفیگ',
    'btn-help': 'راهنمایی',
    'btn-return': 'بازگشت به منوی اصلی',
}

# عملکرد شروع
def start_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    update.message.reply_text(f'سلام {first_name} {last_name}\nبه ربات چک کردن حجم خوش آمدید')
    main_menu_handler(update, context)

# منوی اصلی
def main_menu_handler(update: Update, context: CallbackContext):
    buttons = [
        [messages['btn-check']],
        [messages['btn-help']]
    ]
    update.message.reply_text(
        text=messages['msg-main-menu'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

# شروع بررسی کانفیگ
def check_handler(update: Update, context: CallbackContext):
    update.message.reply_text("لطفاً نام کانفیگ را وارد کنید:")
    return FIRST

# دریافت نام کانفیگ
def get_client_name(update: Update, context: CallbackContext):
    client_name = update.message.text.strip().upper()  
    perform_check(client_name, update, context)
    return ConversationHandler.END

# بررسی کانفیگ
def perform_check(client_name, update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    
    base_url = os.getenv('BASE_URL')
    username = os.getenv('PANEL_USERNAME')
    password = os.getenv('PANEL_PASSWORD')
    login_endpoint = "/login"
    get_client_endpoint = "/panel/api/inbounds/getClientTraffics/"

    login_headers = {"Content-Type": "application/json; charset=utf-8"}
    get_client_headers = {"Accept": "application/json"}

    data = {
        "username": username,
        "password": password
    }

    session = requests.Session()
    login_response = session.post(base_url + login_endpoint, json=data, headers=login_headers)

    if login_response.status_code == 200:
        response_json = login_response.json()
        if response_json.get('success') == True:
            get_client_response = session.get(base_url + get_client_endpoint + client_name, headers=get_client_headers)

            if get_client_response.status_code == 200:
                client_data = get_client_response.json()

                if client_data.get('obj') is None:
                    update.message.reply_text("اسم کانفیگ اشتباه است. لطفاً دوباره تلاش کنید.")
                    return  

                if 'obj' in client_data:
                    save_user_info(chat_id, update.message.chat.username, client_name)
                    acc_mode = 'فعال' if client_data['obj'].get('enable') else 'غیر فعال'
                    total_data = client_data['obj'].get('up', 0) + client_data['obj'].get('down', 0)
                    config_expirytime = client_data['obj'].get('expiryTime')
                    config_name = client_data['obj'].get('email')
                    config_totaltraffic = client_data['obj'].get('total', 0)

                    expiry_info = "نامحدود" if config_expirytime == 0 else jdatetime.datetime.fromtimestamp(config_expirytime / 1000).strftime('%d-%m-%Y')

                    config_totaltraffic_gb = config_totaltraffic / (1024 * 1024 * 1024)
                    total_data_mb = total_data / (1024 * 1024 * 1024)
                    total_data_reming = config_totaltraffic_gb - (total_data / (1024 * 1024 * 1024))

                    total_percent = ((config_totaltraffic_gb - total_data_mb) / config_totaltraffic_gb) * 100
                    progress_bar_length = 10
                    num_blocks = int(progress_bar_length * total_percent / 100)
                    progress_bar = "✅" * num_blocks + "❌" * (progress_bar_length - num_blocks)

                    acc_info = f"اسم کانفیگ : {config_name}\nوضعیت کانفیگ : {acc_mode}\nحجم کل : {config_totaltraffic_gb:.2f}  گیگابایت\nحجم مصرف شده : {total_data_mb:.2f}  گیگابایت\nحجم باقی مانده : {total_data_reming:.2f}  گیگابایت\nحجم باقی مانده به درصد  :  \n {progress_bar} {round(total_percent)}%\nتاریخ انقضا : {expiry_info}"
                    update.message.reply_text(acc_info)
                else:
                    update.message.reply_text("اطلاعاتی برای این کانفیگ پیدا نشد.")
            else:
                update.message.reply_text("خطا در دریافت اطلاعات کانفیگ.")
        else:
            update.message.reply_text("ورود ناموفق بود، لطفاً نام کاربری و رمز عبور را بررسی کنید.")
    else:
        update.message.reply_text("خطا در برقراری ارتباط با سرور. لطفاً دوباره تلاش کنید.")

# ذخیره اطلاعات کاربر
def save_user_info(chat_id, username, client_name):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute('''INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)''', (chat_id, username))
    cursor.execute('''INSERT INTO user_configs (chat_id, client_name) VALUES (?, ?)''', (chat_id, client_name))
    connection.commit()
    connection.close()

# دستورات راهنما
def help_handler(update: Update, context: CallbackContext):
    update.message.reply_text(messages['msg-help'])

# تابع اصلی
def main():
    create_database()

    updater = Updater(token, use_context=True)

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-check']), check_handler)],
        states={
            FIRST: [MessageHandler(Filters.text & ~Filters.command, get_client_name)],
        },
        fallbacks=[],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('start', start_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn-return']), main_menu_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn-help']), help_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
