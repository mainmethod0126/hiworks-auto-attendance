import requests

def login(config_data):
    api_url = config_data['login_api']['url']
    login_id = config_data['login_api']['id']
    login_pw = config_data['login_api']['pw']
    
    headers = {
        "Content-Type": "application/json"
    }
    body = {
        "id": login_id,
        "password": login_pw,
        "ip_security_level": "1"
    }

    return requests.post(api_url, headers=headers, json=body)