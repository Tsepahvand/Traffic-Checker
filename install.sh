#!/bin/bash

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" 

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

loading_animation() {
    local -r msg=$1
    echo -n "$msg"
    for i in {1..5}; do
        echo -n "."
        sleep 0.5
    done
    echo ""
}

# 1. دانلود pip در صورتی که نصب نباشد
loading_animation "Checking if pip is installed"
if ! [ -x "$(command -v pip)" ]; then
    print_warning "pip is not installed. Installing..."
    apt-get update
    apt-get install -y python3-pip
else
    print_success "pip is already installed."
fi

# 2. بررسی و نصب figlet
if ! [ -x "$(command -v figlet)" ]; then
    print_warning "Figlet is not installed. Installing..."
    apt-get update
    apt-get install -y figlet
else
    print_success "Figlet is already installed."
fi

clear
echo -e "${GREEN}"
figlet "TRAFFIC VIEWER" 
echo -e "${NC}"

REPO_URL="https://github.com/Tsepahvand/Traffic-Checker.git"
print_warning "Cloning the repository from $REPO_URL..."
git clone "$REPO_URL" || { print_error "Failed to clone the repository."; exit 1; }

cd Traffic-Checker || { print_error "Failed to enter the repository directory."; exit 1; }

loading_animation "Checking if Docker Compose is up-to-date"
apt-get install -y docker-compose || { print_error "Failed to update Docker Compose."; exit 1; }
print_success "Docker Compose is up-to-date."

read -p "What is your panel type Sanaei or Alireza? (s/a): " panel_type

if [[ "$panel_type" == "s" || "$panel_type" == "S" ]]; then
    print_success "Panel type is Sanaei."
else
    if [[ "$panel_type" == "a" || "$panel_type" == "A" ]]; then
        print_success "Panel type is Alireza. Modifying bot.py..."
        sed -i 's|get_client_endpoint = "/panel/api/inbounds/getClientTraffics/"|get_client_endpoint = "/xui/API/inbounds/getClientTraffics/"|g' bot.py
        print_success "Line 262 in bot.py has been modified."
    else
        print_error "Invalid panel type entered. Exiting."
        exit 1
    fi
fi

read -p "Do you want to convert client names to uppercase (yes/no)? " response


if [[ "$response" == "yes" || "$response" == "y" ]]; then
    print_success "Client names will be converted to uppercase."
else
    print_warning "Client names will not be converted to uppercase. Modifying bot.py..."


    sed -i 's/client_name = update.message.text.strip().upper()/client_name = update.message.text.strip()/g' bot.py
    print_success "Line 250 in bot.py has been modified."
fi


if [ -f "requirements.txt" ]; then
    print_warning "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt || { print_error "Failed to install dependencies."; exit 1; }
else
    print_warning "No requirements.txt found, skipping dependency installation."
fi

loading_animation "Checking if Docker is installed"
if ! [ -x "$(command -v docker)" ]; then
    print_warning "Docker is not installed. Installing..."
    apt-get update
    apt-get install -y docker.io
else
    print_success "Docker is already installed."
fi

loading_animation "Checking if SQLite is installed"
if ! [ -x "$(command -v sqlite3)" ]; then
    print_warning "SQLite is not installed. Installing..."
    apt-get install -y sqlite3
else
    print_success "SQLite is already installed."
fi

DB_PATH="detail.db"
if [ ! -f "$DB_PATH" ]; then
    print_success "Database $DB_PATH created."
    sqlite3 "$DB_PATH" <<EOF
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL,
    owner_id INTEGER NOT NULL
);
EOF
else
    print_success "Database $DB_PATH already exists."
fi

read -p "Enter the bot token: " bot_token
read -p "Enter the owner ID: " owner_id

if [[ -z "$bot_token" || -z "$owner_id" || ! "$owner_id" =~ ^[0-9]+$ ]]; then
    print_error "Invalid input. Please ensure the bot token and owner ID are correct."
    exit 1
fi

sqlite3 "$DB_PATH" <<EOF
INSERT INTO settings (token, owner_id) VALUES ('$bot_token', $owner_id);
EOF
print_success "Information saved."

loading_animation "Running the bot with Docker Compose"
docker-compose up --build -d || { print_error "Docker Compose failed to start."; exit 1; }

read -p "Do you want to set a specific port for WebUI? (y/n): " set_port

if [[ "$set_port" == "y" || "$set_port" == "Y" ]]; then
    read -p "Please enter the port number: " custom_port
    print_success "Changing the port in webUI.py to $custom_port..."
    sed -i "s|app.run(debug=True, host='0.0.0.0', port=5000)|app.run(debug=True, host='0.0.0.0', port=$custom_port)|g" webUI.py
    print_success "Port changed successfully in webUI.py."
else
    print_warning "Skipping port customization for WebUI."
fi

print_success "Running WebUI and Uvicorn..."
nohup python3 webUI.py &  
nohup uvicorn app:app --port 7386 &  
