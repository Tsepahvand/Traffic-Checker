#!/bin/bash


echo "لطفاً توکن ربات را وارد کنید:"
read BOT_TOKEN

echo "لطفاً آدرس پنل را وارد کنید:"
read BASE_URL

echo "لطفاً نام کاربری پنل را وارد کنید:"
read PANEL_USERNAME

echo "لطفاً پسورد پنل را وارد کنید:"
read PANEL_PASSWORD


echo "BOT_TOKEN=$BOT_TOKEN" > .env
echo "BASE_URL=$BASE_URL" >> .env
echo "PANEL_USERNAME=$PANEL_USERNAME" >> .env
echo "PANEL_PASSWORD=$PANEL_PASSWORD" >> .env
echo "اطلاعات به فایل .env ذخیره شد."


if ! command -v docker &> /dev/null
then
    echo "Docker نصب نشده است. لطفا Docker را نصب کنید."
    exit 1
fi


echo "در حال ساخت Docker image..."
docker build -t telegram-bot .

echo "در حال اجرای Docker container..."
docker run --env-file .env --name telegram-bot-container telegram-bot

echo "ربات در Docker راه‌اندازی شد."
