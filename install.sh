#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

print_success() {
    echo -e "${GREEN}$1${RESET}"
}

print_error() {
    echo -e "${RED}$1${RESET}"
}

print_warning() {
    echo -e "${YELLOW}$1${RESET}"
}

print_info() {
    echo -e "${BLUE}$1${RESET}"
}

print_info "Checking if figlet is installed..."
if ! command -v figlet &> /dev/null; then
    print_warning "figlet is not installed. Installing..."
    sudo apt-get install -y figlet
else
    print_success "figlet is already installed."
fi

print_info "Checking if pip is installed..."
if ! command -v pip &> /dev/null; then
    print_warning "pip is not installed. Installing..."
    sudo apt-get install -y python3-pip
else
    print_success "pip is already installed."
fi

figlet "TRAFFIC VIEWER"

REPO_DIR="Traffic-Checker"
if [ -d "$REPO_DIR" ]; then
    print_warning "Repository already exists. Cleaning up and cloning again..."
    rm -rf "$REPO_DIR"
fi

print_info "Cloning GitHub repository..."
git clone https://github.com/Tsepahvand/Traffic-Checker.git

cd "$REPO_DIR"
if [ -f "requirements.txt" ]; then
    print_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found!"
fi

read -p "Do you want to convert client names to uppercase? (yes/no): " convert_to_upper
if [[ "$convert_to_upper" == "no" || "$convert_to_upper" == "n" || "$convert_to_upper" == "NO" || "$convert_to_upper" == "N" || "$convert_to_upper" == "No" ]]; then
    print_info "Modifying bot.py file..."
    sed -i "s/update.message.text.strip().upper()/update.message.text.strip()/g" bot.py

    print_info "Modifying app.py file..."
    sed -i "s/Client = Client.upper()/Client = Client/g" app.py
fi  

read -p "What is your panel type, Sanaei or Alireza? (S/A): " panel_type
if [[ "$panel_type" =~ ^(a|A|alireza|Alireza)$ ]]; then
    print_info "Modifying bot.py and app.py files..."
    sed -i "s|get_client_endpoint = \"/panel/api/inbounds/getClientTraffics/\"|get_client_endpoint = \"/xui/API/inbounds/getClientTraffics/\"|g" bot.py
    sed -i "s|get_client_endpoint = \"/panel/api/inbounds/getClientTraffics/\"|get_client_endpoint = \"/xui/API/inbounds/getClientTraffics/\"|g" app.py
fi  

read -p "Enter the WebUI port (default 5000): " webui_port
if [ -z "$webui_port" ]; then
    webui_port=5000  
fi
print_info "Modifying webUI.py file..."
sed -i "s|app.run(debug=True, host='0.0.0.0', port=5000)|app.run(debug=True, host='0.0.0.0', port=$webui_port)|g" webUI.py

print_info "Checking if Docker is installed..."
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Installing..."
    sudo apt-get install -y docker.io
else
    print_success "Docker is already installed."
fi

print_info "Checking if Docker Compose is installed..."
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose is not installed. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    print_success "Docker Compose is already installed."
    print_info "Updating Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

print_info "Checking if SQLite is installed..."
if ! command -v sqlite3 &> /dev/null; then
    print_warning "SQLite is not installed. Installing..."
    sudo apt-get install -y sqlite3
else
    print_success "SQLite is already installed."
fi

print_info "Checking and creating SQLite database..."
sqlite3 detail.db "CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, token TEXT, owner_id INTEGER);"

read -p "Enter your bot token: " bot_token
read -p "Enter the owner ID: " owner_id

sqlite3 detail.db "INSERT INTO settings (token, owner_id) VALUES ('$bot_token', '$owner_id');"

print_info "Starting the bot with Docker Compose..."
docker-compose up --build -d

print_info "Starting API and webUI..."
nohup python3 webUI.py &
nohup uvicorn app:app --port 7386 &

print_success "Script executed successfully!"
