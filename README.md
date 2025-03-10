# Traffic-Checker
<div dir="rtl">

![Build Status](https://img.shields.io/badge/status-active-success.svg)
![GitHub License](https://img.shields.io/github/license/Tsepahvand/Traffic-Checker)
![GitHub Stars](https://img.shields.io/github/stars/Tsepahvand/Traffic-Checker?style=social)

---
![Python](https://img.shields.io/badge/python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%232496ED.svg?style=for-the-badge&logo=docker&logoColor=white) 
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![Shell](https://img.shields.io/badge/shell-%234EAA25.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)

---

## 📌 فهرست مطالب
- [درباره پروژه](#-درباره-پروژه)
  - [ویژگی‌ها](#-ویژگیها)
  - [عکس‌های پروژه](#%EF%B8%8F-عکس-های-پروژه)
- [طریقه نصب](#-طریقه-نصب)
- [راهنمای استفاده](#-راهنمای-استفاده)
  - [تنظیمات پنل](#-تنظیمات-پنل)
    - [افزودن پنل](#-افزودن-پنل)
    - [حذف پنل](#-حذف-پنل)
  - [تنظیمات Web UI](#-تنظیمات-web-ui)
    - [دامین / ساب دامین](#-دامین--ساب-دامین)
    - [تغییر دامین / ساب دامین](#-تغییر-دامین--ساب-دامین)
    - [گرفتن سرتیفیکت جدید](#-گرفتن-سرتیفیکت-جدید)
    - [تغییر پورت](#-تغییر-پورت)
  - [تنظیمات ربات](#-تنظیمات-ربات)
    - [تغییر مالک ربات](#-تغییر-مالک-ربات)
    - [اضافه کردن ادمین](#-اضافه-کردن-ادمین)
    - [تغییر توکن ربات](#-تغییر-توکن-ربات)


---

## 🎯 درباره پروژه
این پروژه برای **بررسی ترافیک مصرفی کانفیگ‌ها** طراحی شده است. کاربران می‌توانند با وارد کردن **نام کلاینت**، اطلاعات مربوط به **حجم مصرفی، تاریخ انقضا و وضعیت فعال بودن** را دریافت کنند.
مهمترین ویژگی این سرویس بی نام و نشان بودن در طراحی است که به همین خاطر نمایندگان فروش سرویس های شما میتونن بدون دغدغه این پنل یا ربات تلگرامی رو به مشتریان خودشون بدن که از حجم و وضعیت کانفیگ هاشون مطلع بشن

---

## 🚀 ویژگی‌ها
✅ **ربات در کنار WebUI**: استفاده هم از **ربات** و هم **وب اپلیکیشن**  
✅ **بررسی حجم مصرفی**: نمایش حجم کل، مصرف شده و باقی‌مانده  
✅ **وضعیت کانفیگ**: نمایش وضعیت **فعال / غیرفعال**  
✅ **تاریخ انقضا**: نمایش **تاریخ انقضا** کانفیگ  
✅ **پنل مدیریت**: منوی مخصوص برای **مدیریت پنل‌ها و ادمین‌ها**  

---

## 📥 طریقه نصب

### 1️⃣ اجرای دستور نصب در سرور:
```bash
bash <(curl -s https://raw.githubusercontent.com/Tsepahvand/Traffic-Checker/main/install.sh)
```

### 2️⃣ تنظیمات ربات:
```bash
Enter the bot token:
```
🔹 **توکن ربات تلگرام** رو وارد کنید.
توکن رو باید از ربات Bot Father بگیرید : [BotFather](https://t.me/BotFather)

```bash
Enter the owner ID:
```
🔹 **آیدی عددی اکانت تلگرام مالک** رو وارد کنید.
برای بدست آوردن آی دی میتونید از این ربات استفاده کنید: [ID Bot](https://t.me/username_to_id_bot)


### 3️⃣ تنظیمات پنل و کانفیگ‌ها:
```bash
Do you want to convert client names to uppercase (yes/no)?
```
🔹 اگر **نام کانفیگ‌ها** کوچک یا ترکیبی از **حروف کوچک و بزرگ** است `no` را وارد کنید؛ در غیر این صورت `yes`.

```bash
Enter the panel type (sanaei/alireza)? (s/a)
```
🔹 نوع پنل را مشخص کنید (`s` = Sanaei، `a` = Alireza).

### 4️⃣ تنظیمات Web UI:
```bash
Did you want to use a domain for the web UI? (y/n)
```
🔹 اگر می‌خواهید **دامین** داشته باشید `y` را بزنید، در غیر این صورت `n`.

```bash
Do you want to set a port for the web UI? (y/n)
```
🔹 اگر می‌خواهید **پورت** اختصاصی تعیین کنید `y` را بزنید، در غیر این صورت **پورت پیش‌فرض 5000** استفاده می‌شود.

---

## 📌 راهنمای استفاده

### 🔹 تنظیمات پنل
#### ➕ افزودن پنل
1. وارد **ربات** شوید.
2. به بخش **Admin Panel** بروید و روی **"اضافه کردن پنل"** ضربه بزنید.
3. اطلاعات پنل را به صورت زیر وارد کنید:
   ```
   panel_url,username,password
   https://example.com:2053/path,admin,admin
   ```

#### ❌ حذف پنل
1. وارد **ربات** شوید.
2. به بخش **Admin Panel** بروید و روی **"حذف پنل"** ضربه بزنید.
3. لیست پنل‌ها نمایش داده می‌شود، برای حذف **آیدی پنل (عدد پشت آدرس پنل)** را ارسال کنید.

---

### 🔹 تنظیمات Web UI
#### 🌐 تغییر دامین / ساب دامین
```bash
t-ch
```
1. در سرور **دستور بالا** را اجرا کنید.
2. گزینه `2` را انتخاب کنید.
3. `y` را بزنید و **دامین جدید** را وارد کنید.

#### 🔒 گرفتن سرتیفیکت جدید
```bash
t-ch
```
1. گزینه `4` را انتخاب کنید.
2. `y` را بزنید و منتظر دریافت **سرتیفیکت جدید** باشید.

#### 🔄 تغییر پورت
```bash
t-ch
```
1. گزینه `3` را انتخاب کنید.
2. `y` را بزنید و **پورت جدید** را وارد کنید.

---

### 🔹 تنظیمات ربات
#### 👤 تغییر مالک ربات
1. وارد **ربات** شوید.
2. به **Admin Panel** بروید و روی **"تغییر Owner ID"** ضربه بزنید.
3. **آیدی عددی مالک جدید** را ارسال کنید.

#### 👥 اضافه کردن ادمین
1. وارد **ربات** شوید.
2. به **Admin Panel** بروید و روی **"اضافه کردن ادمین"** ضربه بزنید.
3. **آیدی عددی ادمین** را ارسال کنید.

#### 🔑 تغییر توکن ربات
```bash
t-ch
```
1. گزینه `5` را انتخاب کنید.
2. `y` را بزنید و **توکن جدید** را وارد کنید.

---

## 🖼️ عکس های پروژه
![bot](https://github.com/Tsepahvand/Traffic-Checker/blob/main/pic/bot.png)

![web ui](https://github.com/Tsepahvand/Traffic-Checker/blob/main/pic/webui-1.png) 
![web ui](https://github.com/Tsepahvand/Traffic-Checker/blob/main/pic/webui-4.png)
![web ui](https://github.com/Tsepahvand/Traffic-Checker/blob/main/pic/webui-3.png)
![web ui](https://github.com/Tsepahvand/Traffic-Checker/blob/main/pic/webui-2.png)

---

📌 **توسعه‌دهنده:** [Tsepahvand](https://github.com/Tsepahvand)  
🌟 اگر این پروژه براتون مفید بود، لطفاً **⭐️ استار** بدید! 🙌
</div>
