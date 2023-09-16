from datetime import datetime
from today_off_checker import off_check
from login import login
import requests
import time

def attendance_task(none_and_pm_off_target_times, am_off_target_times, config_data):
    while True:
        
        current_time = datetime.today().strftime("%H:%M:%S")
        
        for target_time in none_and_pm_off_target_times:
            
            if current_time == target_time.strftime("%H:%M:%S"):
                
                login_response = login(config_data)
                today_off_info = off_check(config_data, login_response.cookies)
                
                # none || pm-off
                if today_off_info == "none" or today_off_info == "pm-off":
                    result = attendance(config_data, login_response.cookies)
                
                    if result:
                        break    
            
        for target_time in am_off_target_times:
            
            if current_time == target_time.strftime("%H:%M:%S"):
            
                login_response = login(config_data)
                today_off_info = off_check(config_data, login_response.cookies)
            
                # am-off
                if today_off_info == "am-off": 
                    result = attendance(config_data, login_response.cookies)
                    
                    if result:
                        break 
                    
        time.sleep(1)
        
def attendance(config_data, cookies):

    # -----------------------출근--------------------------
    attendance_api_url = config_data['attendance_api']['url']

    headers = {
        "Content-Type": "application/json"
    }
    
    body = {
        "data" : {
            "type": "1"
        }
    }

    login_response = requests.post(attendance_api_url, headers=headers, json=body, cookies=cookies)
    
    return login_response.status_code == 200

