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

if [ -f "requirements.txt" ]; then
    print_warning "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt || { print_error "Failed to install dependencies."; exit 1; }
else
    print_warning "No requirements.txt found, skipping dependency installation."
fi


read -p "Do you want to convert client names to uppercase (yes/no)? " response


if [[ "$response" == "yes" || "$response" == "y" ]]; then
    print_success "Client names will be converted to uppercase."
else
    print_warning "Client names will not be converted to uppercase. Modifying bot.py..."


    sed -i 's/client_name = update.message.text.strip().upper()/client_name = update.message.text.strip()/g' bot.py
    print_success "Line 250 in bot.py has been modified."
fi


loading_animation "Checking if Docker is installed"
if ! [ -x "$(command -v docker)" ]; then
    print_warning "Docker is not installed. Installing..."
    apt-get update
    apt-get install -y docker.io
else
    print_success "Docker is already installed."
fi


loading_animation "Checking if Docker Compose is installed"
if ! [ -x "$(command -v docker-compose)" ]; then
    print_warning "Docker Compose is not installed. Installing..."
    apt-get install -y docker-compose
else
    print_success "Docker Compose is already installed."
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
