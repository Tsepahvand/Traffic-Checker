from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)

translations = {
    'en': {
        'welcome': 'Welcome',
        'enter_email': 'Please enter your config name to get the data:',
        'submit': 'Submit',
        'error': 'Sorry, we could not find the requested data. Please check the ID or try again later.',
        'go_back': 'Go back to home',
        'data_for': 'Data for : ',
        'back_to_home' : 'back to home',
        'of' : 'of',
        'remaining' : 'remaining',
        'consumed' : 'consumed',
        'consumption' : 'consumption',
        'volume' : 'volume',
        'active' : 'active',
        'deactive' : 'deactive',
    },
    'fa': {
        'welcome': 'خوش آمدید',
        'enter_email': 'لطفاً اسم کانفیگ خود را وارد کنید ',
        'submit': 'ارسال',
        'error': 'متاسفیم، ما نتوانستیم اطلاعات درخواست شده را پیدا کنیم. لطفاً شناسه را بررسی کنید یا بعداً دوباره تلاش کنید.',
        'go_back': 'بازگشت به صفحه اصلی',
        'data_for': 'داده‌ها برای : ',
        'back_to_home' : 'برگشت به خانه',
        'of' : 'از',
        'remaining' :'باقی مانده',
        'consumed' : 'مصرف شده',
        'consumption' : 'مصرف',
        'volume' : 'حجم',
        'active' : 'فعال',
        'deactive' : 'غیر فعال',
    }
}

def format_size(size_in_bytes):
    size_in_gb = size_in_bytes / (1024 * 1024 * 1024)
    return f"{size_in_gb:.2f} GB"

def format_time(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000
    return datetime.utcfromtimestamp(timestamp_sec).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/', methods=['GET', 'POST'])
def home():
    lang = request.args.get('lang', 'fa') 
    if request.method == 'POST':
        email_id = request.form.get('email_id')
        return redirect(url_for('index', email_id=email_id, lang=lang))
    return render_template('home.html', lang=lang, translations=translations[lang])

@app.route('/<string:email_id>')
def index(email_id):
    lang = request.args.get('lang', 'en')
    try:
        fastapi_url = f"http://127.0.0.1:7386/cn/?Client={email_id}"
        response = requests.get(fastapi_url)

        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            if message:
                obj = message.get("obj", {})
                up = obj.get("up", 0)
                down = obj.get("down", 0)
                total = obj.get("total", 0)
                email = obj.get("email")
                acc_mode = obj.get("enable")
                expiry_time = obj.get("expiryTime", 0)
                current_time = int(datetime.now().timestamp() * 1000)

                total_gb = total / (1024 ** 3)  
                remaining_time = expiry_time - current_time  
                remaining_days = remaining_time // (1000 * 60 * 60 * 24)  
                remaining_hours = (remaining_time // (1000 * 60 * 60)) % 24  
                remaining_minutes = (remaining_time // (1000 * 60)) % 60  
                remaining_data = total_gb - ((up + down) / (1024 ** 3))
                consumed_data = ((up + down) / (1024 ** 3))

                if total == 0:  
                    first_percent = "نامحدود" if lang == "fa" else "Unlimited"
                    second_percent = f"{translations[lang]['consumption']} : {consumed_data:.2f} گیگابایت  {translations[lang]['consumed']}" if lang == "fa" else f"{translations[lang]['consumption']} : {consumed_data:.2f} GB  {translations[lang]['consumed']}"
                    forth_percent = f"{translations[lang]['volume']} : نامحدود" if lang == "fa" else f"{translations[lang]['volume']} : Unlimited"
                    usage_percentage = 0  
                    third_percent = "0%"  
                else:
                    if expiry_time <= 0:
                        if lang == "fa":
                            first_percent = f"انقضا : نامحدود"
                        else:
                            first_percent = f"Expiry: Unlimited"
                    else:
                        if lang == "fa":
                            first_percent = f"انقضا : {remaining_days} روز {remaining_hours} ساعت {remaining_minutes} دقیقه"
                        else:
                            first_percent = f"{remaining_days} Days {remaining_hours} Hours {remaining_minutes} Minutes"

                    second_percent = f"{translations[lang]['consumption']} : {consumed_data:.2f} گیگابایت {translations[lang]['of']} {total_gb:.2f} گیگابایت {translations[lang]['consumed']}" if lang == "fa" else f"{translations[lang]['consumption']} : {consumed_data:.2f} GB {translations[lang]['of']} {total_gb:.2f} GB {translations[lang]['consumed']}"

                    up_gb = up / (1024 ** 3)  
                    down_gb = down / (1024 ** 3)  

                    if total_gb > 0:
                        usage_percentage = ((total_gb - (up_gb + down_gb)) / total_gb) * 100
                    else:
                        usage_percentage = 0

                    third_percent = f"{usage_percentage:.2f}%"  

                    forth_percent = f"{translations[lang]['volume']} : {remaining_data:.2f} گیگابایت {translations[lang]['remaining']}" if lang == "fa" else f"{translations[lang]['volume']} : {remaining_data:.2f} GB {translations[lang]['remaining']}"

                acc_mode = translations[lang]['active'] if obj.get('enable', False) else translations[lang]['deactive']

                return render_template('index.html', 
                                       email=email,
                                       first_percent=first_percent, 
                                       second_percent=second_percent, 
                                       third_percent=third_percent, 
                                       forth_percent=forth_percent,
                                       acc_mode=acc_mode,
                                       lang=lang, 
                                       translations=translations[lang])

        return render_template('error.html', lang=lang, translations=translations[lang]), 404

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return render_template('error.html', lang=lang, translations=translations[lang]), 500

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)

