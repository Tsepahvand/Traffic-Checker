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

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    print_warning "Virtual environment not found. Creating one..."
    if ! dpkg -l | grep -q python3-venv; then
        print_warning "python3-venv not found. Installing..."
        sudo apt install -y python3-venv || { print_error "Failed to install python3-venv."; exit 1; }
    fi
    python3 -m venv "$VENV_DIR" || { print_error "Failed to create virtual environment."; exit 1; }
fi

source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated."

if ! [ -x "$(command -v pip)" ]; then
    print_warning "pip is not installed. Installing pip..."
    python3 -m ensurepip --upgrade || { print_error "Failed to install pip."; exit 1; }
else
    print_success "pip is already installed."
fi

REPO_URL="https://github.com/Tsepahvand/Traffic-Checker.git"
TRAFFIC_DIR="/root/Traffic-Checker"

if [ -d "$TRAFFIC_DIR" ]; then
    print_warning "$TRAFFIC_DIR already exists. Removing it..."
    rm -rf "$TRAFFIC_DIR" || { print_error "Failed to remove existing directory."; exit 1; }
fi

print_warning "Cloning the repository from $REPO_URL..."
git clone "$REPO_URL" || { print_error "Failed to clone the repository."; exit 1; }

cd "$TRAFFIC_DIR" || { print_error "Failed to enter the repository directory."; exit 1; }

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


loading_animation "Checking if Docker Compose is installed"
if ! [ -x "$(command -v docker-compose)" ]; then
    print_warning "Docker Compose is not installed. Installing..."
    apt-get install -y docker-compose
else
    print_success "Docker Compose is already installed."
fi


loading_animation "Checking if curl is installed"
if ! command -v curl &> /dev/null; then
    echo "⚠️ curl not found! Installing..."
    apt update && apt install -y curl
    echo "✅ curl installed successfully."
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


sqlite3 "detail.db" <<EOF
ALTER TABLE settings ADD COLUMN upper TEXT;
ALTER TABLE settings ADD COLUMN panel_type TEXT;
ALTER TABLE settings ADD COLUMN public_ip TEXT;
EOF

sqlite3 "detail.db" <<EOF
INSERT INTO settings (token, owner_id, upper, panel_type, public_ip) 
VALUES ('$bot_token', $owner_id, NULL, NULL, NULL);
EOF

print_success "Information saved."

read -p "Do you want to convert client names to uppercase (yes/no)? " upper_response
if [[ "$upper_response" == "yes" || "$upper_response" == "y" ]]; then
    sqlite3 "detail.db" "UPDATE settings SET upper = 'yes';"
    print_success "Client names will be converted to uppercase."
else
    sqlite3 "detail.db" "UPDATE settings SET upper = 'no';"
    print_warning "Client names will not be converted to uppercase."
fi

read -p "Enter the panel type (sanaei/alireza)? (s/a): " panel_type
case $panel_type in
    s|S|sanaei|Sanaei)
        PANEL_TYPE="sanaei"
        ;;
    a|A|alireza|Alireza)
        PANEL_TYPE="alireza"
        ;;
    *)
        print_error "Invalid panel type. Please enter 'sanaei' or 'alireza'."
        exit 1
        ;;
esac
sqlite3 "detail.db" "UPDATE settings SET panel_type = '$PANEL_TYPE';"
print_success "Panel type saved in the database: $PANEL_TYPE"

install_certbot() {
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}Certbot is not installed. Installing...${NC}"
        sudo apt update
        sudo apt install -y certbot
        if ! command -v certbot &> /dev/null; then
            echo -e "${RED}Failed to install certbot. Please install it manually.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Certbot installed successfully.${NC}"
    else
        echo -e "${GREEN}Certbot is already installed.${NC}"
    fi
}

get_ssl_certificate() {
    local domain=$1
    echo -e "${GREEN}Getting SSL certificate for domain: $domain${NC}"
    sudo certbot certonly --standalone --agree-tos --non-interactive --email admin@$domain -d $domain
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}SSL certificate obtained successfully.${NC}"
        CERT_PATH="/etc/letsencrypt/live/$domain/fullchain.pem"
        KEY_PATH="/etc/letsencrypt/live/$domain/privkey.pem"
        sqlite3 "detail.db" "UPDATE settings SET cert_path = '$CERT_PATH', key_path = '$KEY_PATH';"
        echo -e "${GREEN}Certificate paths saved in the database.${NC}"
        
        COMPOSE_FILE="/root/Traffic-Checker/docker-compose.yml"
        if [[ -f "$COMPOSE_FILE" ]]; then
            sed -i "s|/etc/letsencrypt/live/[^:]*|/etc/letsencrypt/live/$domain|g" "$COMPOSE_FILE"
            sed -i "s|/etc/letsencrypt/archive/[^:]*|/etc/letsencrypt/archive/$domain|g" "$COMPOSE_FILE"
            echo -e "${GREEN}Updated $COMPOSE_FILE with new domain: $domain${NC}"
        else
            echo -e "${RED}Error: $COMPOSE_FILE not found!${NC}"
        fi
    else
        echo -e "${RED}Failed to obtain SSL certificate.${NC}"
        exit 1
    fi
}


read -p "Did you want to use a domain for the web UI? (y/n): " use_domain
if [[ "$use_domain" =~ ^(y|Y|yes|YES)$ ]]; then
    read -p "Enter your domain/subdomain: " domain
    PUBLIC_IP="$domain"
    install_certbot
    get_ssl_certificate "$domain"
else
    PUBLIC_IP=$(curl -s https://api.ipify.org)
    echo -e "${YELLOW}Using public IP: $PUBLIC_IP${NC}"
fi
sqlite3 "detail.db" "UPDATE settings SET public_ip = '$PUBLIC_IP';"
echo -e "${GREEN}Public IP/Domain saved in the database: $PUBLIC_IP${NC}"

find_free_port() {
    local port=5000
    while nc -z localhost "$port" &>/dev/null; do
        port=$((port + 1))
    done
    echo "$port"
}

read -p "Do you want to set a port for the web UI? (y/n): " set_port
if [[ "$set_port" =~ ^(y|Y|yes|YES)$ ]]; then
    read -p "Enter the port for the web UI (default: 5000): " webui_port
    if [[ -z "$webui_port" ]]; then
        webui_port=$(find_free_port)
        print_warning "No port specified. Using the first available port: $webui_port"
    else
        if nc -z localhost "$webui_port" &>/dev/null; then
            print_error "Port $webui_port is already in use. Please choose another port."
            exit 1
        fi
    fi
else
    webui_port=$(find_free_port)
    print_warning "No port specified. Using the first available port: $webui_port"
fi
export WEBUI_PORT=$webui_port


sqlite3 "detail.db" "ALTER TABLE settings ADD COLUMN port INTEGER;"
sqlite3 "detail.db" "UPDATE settings SET port = $webui_port;"
print_success "Web UI port saved in the database: $webui_port"



if [[ -f "/root/Traffic-Checker/t-ch" ]]; then
    chmod +x /root/Traffic-Checker/t-ch
    echo "File /root/Traffic-Checker/t-ch is now executable."
else
    echo "Error: File /root/Traffic-Checker/t-ch not found."
    exit 1
fi

if [[ ":$PATH:" != *":/root/Traffic-Checker:"* ]]; then
    echo 'export PATH="$PATH:/root/Traffic-Checker"' >> ~/.bashrc
    echo "Added /root/Traffic-Checker to PATH in ~/.bashrc."
else
    echo "/root/Traffic-Checker is already in PATH."
fi

source ~/.bashrc
echo "Applied changes to ~/.bashrc."

sed -i "s/\${WEBUI_PORT}/$webui_port/g" "$TRAFFIC_DIR/docker-compose.yml"
print_success "Port updated in docker-compose.yml."

loading_animation "Running the bot with Docker Compose"
docker-compose up --build -d || { print_error "Docker Compose failed to start."; exit 1; }
