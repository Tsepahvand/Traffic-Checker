from fastapi import FastAPI, HTTPException
import requests
import sqlite3

app = FastAPI()

def get_db_connection():
    return sqlite3.connect("detail.db")

def get_panels():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT base_url, username, password FROM panels')  
    panels = cursor.fetchall()
    connection.close()
    return panels
    
def get_panel_type():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT panel_type FROM settings WHERE id = 1')  
    result = cursor.fetchone() 
    connection.close()

    return result[0] if result else None

def get_upper_or_no():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT upper FROM settings WHERE id = 1')  
    result = cursor.fetchone() 
    connection.close()
    
    return result[0] if result else None

@app.get('/cn/')
def check(Client: str):

    panels = get_panels()
    panel_type = get_panel_type()
    name_upper = get_upper_or_no()

    final_response = None
    if name_upper == 'yes':
        Client =  Client.upper() 
    else:
        Client = Client


    for base_url, username, password in panels:
        login_endpoint = "/login"
        if panel_type == 'sanaei':
            get_client_endpoint = "/panel/api/inbounds/getClientTraffics/"
        elif panel_type == 'alireza':
            get_client_endpoint = "/xui/API/inbounds/getClientTraffics/"

        session = requests.Session()

        login_response = session.post(base_url + login_endpoint, json={"username": username, "password": password})
        if login_response.status_code == 200 and login_response.json().get('success') == True:
            get_client_response = session.get(base_url + get_client_endpoint + Client)
            if get_client_response.status_code == 200 and get_client_response.json().get('obj'):
                final_response = get_client_response.json()
                break

    if final_response:
        return {'message': final_response}
    else:
        raise HTTPException(status_code=404, detail="Client not found or authentication failed")