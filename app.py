from fastapi import FastAPI, HTTPException
import requests
import sqlite3

app = FastAPI()

def get_panels():
    with sqlite3.connect("detail.db") as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT base_url, username, password FROM panels')  
        return cursor.fetchall()

@app.get('/cn/')
def check(Client: str):
    panels = get_panels()
    final_response = None
    Client = Client.upper()

    for base_url, username, password in panels:
        login_endpoint = "/login"
        get_client_endpoint = "/panel/api/inbounds/getClientTraffics/"

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
