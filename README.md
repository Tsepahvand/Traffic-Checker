# Traffic-Checker



این ربات تلگرام برای بررسی ترافیک مصرفی کانفیگ ها طراحی شده است. شما می‌توانید از طریق وارد کردن نام کلاینت، اطلاعات مربوط به حجم مصرفی، تاریخ انقضا و وضعیت فعال بودن آن را دریافت کنید.

---

## ویژگی‌ها

- **بررسی حجم مصرفی**: نمایش حجم کل، حجم مصرف شده و حجم باقی‌مانده.
- **وضعیت کانفیگ**: نمایش وضعیت فعال یا غیرفعال بودن کانفیگ.
- **تاریخ انقضا**: نمایش تاریخ انقضای کانفیگ.
- ![نمونه تصویر](https://github.com/Tsepahvand/Traffic-Checker/blob/main/example.png?raw=true)


---

## طریقه نصب

ابتدا مخزن را کلون کنید و وارد پوشه پروژه شوید:

```bash
git clone https://github.com/Tsepahvand/Traffic-Checker.git
cd Traffic-Checker/
```
سپس فایل .env را برای وارد کردن اطلاعات حساس مانند توکن و اطلاعات ورود به پنل ایجاد کنید:

```bash
nano .env
```
مقادیر زیر را در فایل .env وارد کنید:

```env
BOT_TOKEN= توکن ربات
BASE_URL= ادرس پنل
PANEL_USERNAME= نام کاربری ورود به پنل
PANEL_PASSWORD= رمز ورود به پنل
```
نکته: آدرس پنل را باید به یکی از شکل‌های زیر وارد کنید:

• `https://localhost:port/path` 

• `https://localhost:port` 

• `http://localhost:port/path` 

• `http://localhost:port`

پس از ویرایش و ذخیره فایل .env، با استفاده از دستور زیر کانتینر داکر را بسازید و اجرا کنید:

```bash
docker-compose up --build -d
```
---
## نکته مهم درباره نام کانفیگ ها

اگر نام کانفیگ های شما شامل حروف کوچک یا ترکیبی از حروف کوچک و بزرگ است، لطفاً خط 74 فایل bot.py را به شکل زیر تغییر دهید تا به درستی کار کند:
```python
client_name = update.message.text
```
