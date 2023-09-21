from datetime import datetime
import requests

def off_check(config_data, cookies):
    # if (config_data['use_in_progress_approvals']) :
    #     max_page_number = get_in_progress_approval_max_page_number(config_data, cookies)
    #     get_today_vacation_approval_by_in_progress_approval(config_data, cookies, max_page_number)
    
    
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


def get_today_vacation_approval_by_in_progress_approval(config_data, cookies, max_page_number):
    
    in_progress_approval_api = config_data['in_progress_approval_api']['url']
    
    vacation_approvals = []
    
    current_date_tmp = datetime.today().strftime("%Y-%m-%d")
    
    date_object = datetime.strptime(current_date_tmp, '%Y-%m-%d')
    
    
    kor_date = date_to_kor_date_format(date_object)
    sample = "청구"
    
    for current_page_number in range(1, max_page_number + 1):
        payload = {
            "page": str(current_page_number),
            "pStatus": "P",
            "pMenu": "get_document_list"
        }

        response = requests.post(in_progress_approval_api, data=payload, cookies=cookies).json()
        
        for approval in response["result"]:
            # if approval in "휴가 신청" and approval in kor_date:
            if "치과" in approval["title"] and sample in approval["title"] :
                vacation_approvals.append(response)



def get_in_progress_approval_max_page_number(config_data, cookies):
    in_progress_approval_api = config_data['in_progress_approval_api']['url']
    

    payload = {
        "pMenu": "get_approval_count"
    }

    approval_count = requests.post(in_progress_approval_api, data=payload, cookies=cookies).json()
    in_progress_approval_count = approval_count["result"]["p"]

    # 한페이지의 리스트 size 는 15가 박혀있는 듯
    table_item_size = 15


    # 페이지는 1부터 시작합니다 그렇기 때문에 + 1합니다
    max_page_number = int((in_progress_approval_count) / table_item_size) + 1

    return max_page_number

def date_to_kor_date_format(date):
    
    # 날짜 객체에서 년, 월, 일을 추출
    year = date.year
    month = date.month
    day = date.day
    
    # 변환된 텍스트 반환
    kor_date = f"{year}년 {month}월 {day}일"
    return kor_date



