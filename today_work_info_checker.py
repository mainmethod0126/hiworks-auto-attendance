from today_off_checker import off_check
from datetime import datetime

import requests

def get_today_off_info(url, cookies):

    # 현재 날짜를 가져오기
    current_date = datetime.today().strftime("%Y-%m-%d")

    # 금일 근무 정보 가져오기
    params = {
        "filter[work_date][gte]": current_date,
        "filter[work_date][lte]": current_date,
        "page[limit]": 25,
        "page[offset]": 0
    }

    today_work_info_response = requests.get(url, params=params, cookies=cookies)

    # JSON 형식의 응답을 파이썬 딕셔너리로 변환
    today_work_info = today_work_info_response.json()

    # user_work_data에 접근
    user_work_data = today_work_info['data']['user_work_data']

    return off_check(user_work_data, current_date)
