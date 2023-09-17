from datetime import datetime
import requests

def off_check(config_data, cookies):
    
    current_date = datetime.today().strftime("%Y-%m-%d")
    
    # 금일 근무 정보 가져오기
    work_calendar_api_url = config_data['work_calendar_api']['url']
    params = {
        "filter[work_date][gte]": current_date,
        "filter[work_date][lte]": current_date,
        "page[limit]": 25,
        "page[offset]": 0
    }

    today_work_info_response = requests.get(work_calendar_api_url, params=params, cookies=cookies)

    # JSON 형식의 응답을 파이썬 딕셔너리로 변환
    today_work_info = today_work_info_response.json()

    # user_work_data에 접근
    datas = today_work_info['data']['user_work_data']
    
    for data in datas:
        if data['work_date'] == current_date:
            if data['day_off_type'] != 0: # 공휴일, 주말일 경우 0이 아님
                return "full-off"
            if 'vacation_data' not in data: # 휴가 사용 여부를 위한 판단
                return "none"
            else: # 휴가 사용 시, 오전반차, 오후반차, 연차 구분
                for vacation in data['vacation_data']:
                    if vacation['time_type'] == 'H':
                        if vacation['start_time'] == '09:00:00':
                            return "am-off"
                        elif vacation['start_time'] == '14:00:00':
                            return "pm-off"
                    elif vacation['time_type'] == 'D':
                        return "full-off"
    return "Invalid work_date"