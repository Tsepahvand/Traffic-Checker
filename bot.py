from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import sqlite3
import requests
import jdatetime
import logging
import uuid
import random
import json
from datetime import datetime, timedelta

logging.basicConfig(filename='log.log', filemode='a', level=logging.INFO, format='%(asctime)s-%(filename)s-%(message)s')



FIRST, SECOND , REMOVE_ADMIN, REMOVE_PANEL, CHANGE_OWNER = range(5)



def get_db_connection():
    return sqlite3.connect("detail.db")

def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_url TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    



    cursor.execute('''
        CREATE TABLE IF NOT EXISTS panels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_url TEXT,
            username TEXT,
            password TEXT
        )
    ''')


    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS owner (
            id INTEGER PRIMARY KEY,
            owner_id INTEGER UNIQUE
        )
    ''')
    
    connection.commit()
    connection.close()

def get_bot_info():
    connection = sqlite3.connect('detail.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT token , owner_id FROM settings WHERE id = 1')
    bot_info = cursor.fetchone()  


    connection.close()
    
    if bot_info:
        return bot_info  
    else:
        return None 

def get_panels():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT base_url, username, password FROM panels')  
    panels = cursor.fetchall()
    connection.close()
    return panels

def get_owner():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT owner_id FROM settings WHERE id = 1')
    owner = cursor.fetchone()
    connection.close()
    return owner[0] if owner else None

def get_admins():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT admin_id FROM admins')
    admins = [row[0] for row in cursor.fetchall()]
    connection.close()
    return admins

# پیام‌ها
messages = {
    'msg-main-menu': 'منوی اصلی :\nبرای لغو هر عملیات، دستور /cancel را وارد کنید.',
    'msg-help': 'سلام به کانفیگ چکر خوش اومدید\nبا زدن روی بررسی کانفیگ و بعد نوشتن اسم کانفیگتون\nاز اطلاعات اون مطلع شوید\nاگر می‌خواهید از عملیات خارج شوید، دستور /cancel را وارد کنید.',
    'btn-check': 'بررسی کانفیگ',
    'btn-help': 'راهنمایی',
    'btn-admin': 'admin panel',
    'btn-return': 'بازگشت به منوی اصلی',
    'btn-add-panel': 'اضافه کردن پنل',
    'btn-add-admin': 'اضافه کردن ادمین',
    'msg-add-panel': 'لطفاً اطلاعات پنل را به شکل "URL,USERNAME,PASSWORD" وارد کنید:\nبرای لغو عملیات، دستور /cancel را وارد کنید.',
    'msg-add-admin': 'لطفاً آیدی عددی ادمین جدید را وارد کنید:\nبرای لغو عملیات، دستور /cancel را وارد کنید.',
    'btn-remove-admin': 'حذف مدیر',
    'btn-remove-panel': 'حذف پنل',
    'btn-change-owner': 'تغییر Owner ID',
    'msg-remove-admin': 'مدیر مورد نظر برای حذف را انتخاب کنید:\nبرای لغو عملیات، دستور /cancel را وارد کنید.',
    'msg-remove-panel': 'پنل مورد نظر برای حذف را انتخاب کنید:\nبرای لغو عملیات، دستور /cancel را وارد کنید.',
    'msg-change-owner': 'لطفاً Owner ID جدید را وارد کنید:\nبرای لغو عملیات، دستور /cancel را وارد کنید.',
    'msg-admin-deleted': 'مدیر با موفقیت حذف شد.',
    'msg-panel-deleted': 'پنل با موفقیت حذف شد.',
    'msg-owner-changed': 'Owner ID با موفقیت تغییر یافت.',
    'msg-invalid-input': 'ورودی نامعتبر. لطفاً دوباره تلاش کنید.',
}

def start_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    update.message.reply_text(f'سلام {update.message.chat.first_name}\n به ربات چک کردن حجم خوش آمدید')
    main_menu_handler(update, context)
    



def main_menu_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    owner_id = get_owner()
    admins = get_admins()

    if chat_id == owner_id or chat_id in admins:
        buttons = [
            [messages['btn-check']],
            [messages['btn-help']],
            [messages['btn-admin']],  
        ]
    else:
        buttons = [
            [messages['btn-check']],
            [messages['btn-help']]
        ]

    update.message.reply_text(
        text=messages['msg-main-menu'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

def is_owner(chat_id):
    return chat_id == get_owner()




def is_admin(chat_id):
    return chat_id in get_admins() or is_owner(chat_id)






def admin_menu_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    buttons = []

    if is_admin(chat_id):
     buttons.extend([[messages['btn-add-panel']], [messages['btn-remove-panel']],
                     [messages['btn-add-admin'],messages['btn-remove-admin']],
                     [messages['btn-return']]])

    if is_owner(chat_id):
        buttons.extend([[messages['btn-change-owner']]])

    update.message.reply_text(
        text="پنل ادمین :",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

    






def add_admin(admin_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT OR IGNORE INTO admins (admin_id) VALUES (?)', (admin_id,))
    connection.commit()
    connection.close()




def add_panel(base_url, username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO panels (base_url, username, password) VALUES (?, ?, ?)', 
                   (base_url, username, password))
    connection.commit()
    connection.close()




def add_admin_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if is_owner(chat_id) or is_admin(chat_id):
        update.message.reply_text(messages['msg-add-admin'])
        return SECOND
    else:
        update.message.reply_text("شما اجازه انجام این کار را ندارید.")



def save_admin(update: Update, context: CallbackContext):
    try:
        admin_id = int(update.message.text.strip())
        add_admin(admin_id)
        update.message.reply_text("ادمین جدید با موفقیت اضافه شد.")
    except ValueError:
        update.message.reply_text("لطفاً آیدی عددی معتبر وارد کنید.")
    return ConversationHandler.END





def check_handler(update: Update, context: CallbackContext):
    update.message.reply_text("لطفاً نام کانفیگ را وارد کنید:")
    return FIRST




def get_client_name(update: Update, context: CallbackContext):
    client_name = update.message.text.strip().upper()  
    perform_check(client_name, update, context)
    return ConversationHandler.END

def perform_check(client_name, update: Update, context: CallbackContext):

    chat_id = update.message.chat_id
    panels = get_panels()
    found = False

    for base_url, username, password in panels:
        login_endpoint = "/login"
        get_client_endpoint = "/panel/api/inbounds/getClientTraffics/"
        session = requests.Session()

        login_response = session.post(base_url + login_endpoint, json={"username": username, "password": password})
        if login_response.status_code == 200:
            response_json = login_response.json()
            if response_json.get('success') == True:
                get_client_response = session.get(base_url + get_client_endpoint + client_name)

                if get_client_response.status_code == 200:
                    client_data = get_client_response.json()

                    if client_data.get('obj') is not None:
                        found = True
                        acc_mode = 'فعال' if client_data['obj'].get('enable') else 'غیر فعال'
                        total_data = client_data['obj'].get('up', 0) + client_data['obj'].get('down', 0)
                        config_expirytime = client_data['obj'].get('expiryTime')
                        config_name = client_data['obj'].get('email')
                        config_totaltraffic = client_data['obj'].get('total', 0)

                        expiry_info = "نامحدود" if config_expirytime == 0 else jdatetime.datetime.fromtimestamp(config_expirytime / 1000).strftime('%d-%m-%Y')

                        config_totaltraffic_gb = config_totaltraffic / (1024 * 1024 * 1024)
                        
                        if config_totaltraffic_gb == 0:  
                            config_totaltraffic_gb = 'نامحدود'
                            total_data_mb = total_data / (1024 * 1024 * 1024)  
                            total_data_reming = 'نامحدود'
                            total_percent = None
                            progress_bar = "نامحدود"
                        else:  
                            total_data_mb = total_data / (1024 * 1024 * 1024)
                            total_data_reming = config_totaltraffic_gb - total_data_mb
                            total_percent = ((config_totaltraffic_gb - total_data_mb) / config_totaltraffic_gb) * 100
                            progress_bar_length = 10
                            num_blocks = int(progress_bar_length * total_percent / 100)
                            progress_bar = "█" * num_blocks + "░" * (progress_bar_length - num_blocks)

                        acc_info = f"اسم کانفیگ : {config_name}\nوضعیت کانفیگ : {acc_mode}\n"

                        if config_totaltraffic_gb == 'نامحدود':
                            acc_info += f"حجم کل : {config_totaltraffic_gb}\n"
                            acc_info += f"حجم باقی مانده : {total_data_reming}\n"
                            acc_info += f"حجم مصرف شده : {total_data_mb:.2f} گیگابایت\n"
                        else:
                            acc_info += f"حجم کل : {config_totaltraffic_gb:.2f}  گیگابایت\n"
                            acc_info += f"حجم باقی مانده : {total_data_reming:.2f}  گیگابایت\n"
                            acc_info += f"حجم مصرف شده : {total_data_mb:.2f} گیگابایت\n"

                        if total_percent is not None:
                            acc_info += f"حجم باقی مانده به درصد :\n {progress_bar} {round(total_percent)}%\n"

                        acc_info += f"تاریخ انقضا : {expiry_info}"
                        update.message.reply_text(acc_info)
                        break
            else:
                update.message.reply_text("ورود به پنل ناموفق بود.")
    
    if not found:
        update.message.reply_text("کانفیگ یافت نشد.")

def help_handler(update: Update, context: CallbackContext):
    update.message.reply_text(messages['msg-help'])

def remove_admin_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if is_owner(chat_id) or is_admin(chat_id):
        admins = get_admins()
        if not admins:
            update.message.reply_text("هیچ مدیری برای حذف وجود ندارد.")
            return ConversationHandler.END

        admin_list = "\n".join([f"{i+1}- {admin}" for i, admin in enumerate(admins)])
        update.message.reply_text(f"{messages['msg-remove-admin']}\n{admin_list}")
        return REMOVE_ADMIN
    else:
        update.message.reply_text("شما اجازه انجام این کار را ندارید.")
        return ConversationHandler.END

def delete_admin(update: Update, context: CallbackContext):
    try:
        selected_index = int(update.message.text.strip()) - 1
        admins = get_admins()

        if 0 <= selected_index < len(admins):
            admin_to_delete = admins[selected_index]
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('DELETE FROM admins WHERE admin_id = ?', (admin_to_delete,))
            connection.commit()
            connection.close()

            update.message.reply_text(messages['msg-admin-deleted'])
        else:
            update.message.reply_text(messages['msg-invalid-input'])
    except ValueError:
        update.message.reply_text(messages['msg-invalid-input'])
    return ConversationHandler.END

def remove_panel_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if is_admin(chat_id):
        panels = get_panels()
        if not panels:
            update.message.reply_text("هیچ پنلی برای حذف وجود ندارد.")
            return ConversationHandler.END

        panel_list = "\n".join([f"{i+1}- {panel[0]}" for i, panel in enumerate(panels)])
        update.message.reply_text(f"{messages['msg-remove-panel']}\n{panel_list}")
        return REMOVE_PANEL
    else:
        update.message.reply_text("شما اجازه انجام این کار را ندارید.")
        return ConversationHandler.END

def delete_panel(update: Update, context: CallbackContext):
    try:
        selected_index = int(update.message.text.strip()) - 1
        panels = get_panels()

        if 0 <= selected_index < len(panels):
            panel_to_delete = panels[selected_index][0]
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('DELETE FROM panels WHERE base_url = ?', (panel_to_delete,))
            connection.commit()
            connection.close()

            update.message.reply_text(messages['msg-panel-deleted'])
        else:
            update.message.reply_text(messages['msg-invalid-input'])
    except ValueError:
        update.message.reply_text(messages['msg-invalid-input'])
    return ConversationHandler.END

def change_owner_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if is_owner(chat_id):
        update.message.reply_text(messages['msg-change-owner'])
        return CHANGE_OWNER
    else:
        update.message.reply_text("شما اجازه انجام این کار را ندارید.")
        return ConversationHandler.END

def update_owner(update: Update, context: CallbackContext):
    try:
        new_owner_id = int(update.message.text.strip())
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('UPDATE settings SET owner_id = ? WHERE id = 1', (new_owner_id,))
        connection.commit()
        connection.close()

        update.message.reply_text(messages['msg-owner-changed'])
    except ValueError:
        update.message.reply_text(messages['msg-invalid-input'])
    return ConversationHandler.END

def add_panel_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if is_admin(chat_id):
        update.message.reply_text(messages['msg-add-panel'])
        return FIRST
    else:
        update.message.reply_text("شما اجازه انجام این کار را ندارید.")
        return ConversationHandler.END

def save_panel(update: Update, context: CallbackContext):
    panel_info = update.message.text.strip()
    try:
        base_url, username, password = map(str.strip, panel_info.split(","))
        add_panel(base_url, username, password)  
        update.message.reply_text("پنل با موفقیت اضافه شد.")
    except ValueError:
        update.message.reply_text("فرمت وارد شده صحیح نیست. لطفاً دوباره تلاش کنید.")
        return FIRST  # کاربر را به همان مرحله برگردانید تا دوباره تلاش کند
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("عملیات لغو شد. می‌توانید از گزینه‌های دیگر استفاده کنید.")
    return ConversationHandler.END  

def setup_conversation_handlers(updater):
    add_panel_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-add-panel']), add_panel_handler)],
        states={
            FIRST: [MessageHandler(Filters.text & ~Filters.command, save_panel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    remove_admin_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-remove-admin']), remove_admin_handler)],
        states={
            REMOVE_ADMIN: [MessageHandler(Filters.text & ~Filters.command, delete_admin)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    remove_panel_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-remove-panel']), remove_panel_handler)],
        states={
            REMOVE_PANEL: [MessageHandler(Filters.text & ~Filters.command, delete_panel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    change_owner_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-change-owner']), change_owner_handler)],
        states={
            CHANGE_OWNER: [MessageHandler(Filters.text & ~Filters.command, update_owner)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    check_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-check']), check_handler)],
        states={
            FIRST: [MessageHandler(Filters.text & ~Filters.command, get_client_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    add_panel_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-add-panel']), add_panel_handler)],
        states={
            FIRST: [MessageHandler(Filters.text & ~Filters.command, save_panel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    add_admin_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn-add-admin']), add_admin_handler)],
        states={
            SECOND: [MessageHandler(Filters.text & ~Filters.command, save_admin)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    updater.dispatcher.add_handler(add_panel_conv_handler)
    updater.dispatcher.add_handler(add_admin_conv_handler)

    updater.dispatcher.add_handler(add_panel_conv_handler)
    updater.dispatcher.add_handler(remove_admin_conv_handler)
    updater.dispatcher.add_handler(remove_panel_conv_handler)
    updater.dispatcher.add_handler(change_owner_conv_handler)
    updater.dispatcher.add_handler(check_conv_handler)


def main():
    create_tables()
    bot_info = get_bot_info()
    if bot_info:
        token = bot_info[0]
        updater = Updater(token, use_context=True)
    setup_conversation_handlers(updater)

    



    updater.dispatcher.add_handler(CommandHandler('start', start_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn-return']), main_menu_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn-help']), help_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn-admin']), admin_menu_handler))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

