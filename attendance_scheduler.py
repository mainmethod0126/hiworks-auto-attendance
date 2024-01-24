from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor




from datetime import datetime
from api_client import ApiClient
from config_module import load_config, get_config_data
from target_time_generator import generate_target_times

import time
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# 순차적으로 실행되는 스케줄러 설정
executors = {
    'default': ThreadPoolExecutor(1)  # 스레드 풀의 크기를 1로 설정
}



# 스케줄러의 스레드를 하나로 지정하여, 동일 시간으로 등록되어있을 경우 병렬이 아닌 순차적 실행되 되도록 하기 위함
scheduler = BackgroundScheduler(executors=executors)
scheduler.start()

class ApiErrException(Exception):
    pass


def api_err_handler():
    raise ApiErrException("API 호출 결과가 Failed입니다")




def run():
    print("지금부터 출근 스케줄러가 실행됩니다!")
    print("target times 에 출근을 시도하니 해당 시간 이후에 출근 여부 확인해주시길 바랍니다.")
    
    reset_scheduler()



def reset_target_times():
    config_data = get_config_data()

    # -----------------------target times 생성--------------------------
    print("start reset target times")

    none_and_pm_off_start_time = datetime.strptime(
        config_data["none_and_pm_off_range"]["start_time"], "%H:%M:%S"
    )
    none_and_pm_off_end_time = datetime.strptime(
        config_data["none_and_pm_off_range"]["end_time"], "%H:%M:%S"
    )
    am_off_start_time = datetime.strptime(
        config_data["am_off_range"]["start_time"], "%H:%M:%S"
    )
    am_off_end_time = datetime.strptime(
        config_data["am_off_range"]["end_time"], "%H:%M:%S"
    )
    interval = config_data["interval"]
    retry_count = config_data["retry_count"]

    global none_and_pm_off_target_times
    global am_off_target_times

    none_and_pm_off_target_times = generate_target_times(
        none_and_pm_off_start_time, none_and_pm_off_end_time, interval, retry_count
    )
    am_off_target_times = generate_target_times(
        am_off_start_time, am_off_end_time, interval, retry_count
    )

    for target_time in none_and_pm_off_target_times:
        print("none_and_pm_off_target_times : " + target_time.strftime("%H:%M:%S"))

    for target_time in am_off_target_times:
        print("am_off_target_times : " + target_time.strftime("%H:%M:%S"))

def reset_scheduler():

    scheduler.remove_all_jobs()
    
    reset_target_times()
    
    for target_time in none_and_pm_off_target_times:
        scheduler.add_job(
            none_and_pm_off_attendance,
            "date",
            run_date=target_time,
            id=target_time.strftime("%H:%M:%S"),
            args=[target_time, reset_scheduler]
        )

    for target_time in am_off_target_times:
        scheduler.add_job(
            am_off_attendance,
            "date",
            run_date=target_time,
            id=target_time.strftime("%H:%M:%S"),
            args=[target_time, reset_scheduler]
        )
        





# 정상 출근 / 오후 반차
def none_and_pm_off_attendance(current_time, callback_succeed_attendance):
    login_result = ApiClient.get_instance().login()

    if login_result.is_err():
        logging.error("로그인에 실패하였습니다")
        return False

    today_off_info_result = ApiClient.get_instance().off_check(
        login_result.ok().cookies  # type: ignore
    )

    if today_off_info_result.is_err():
        logging.error("금일 휴가 사용 여부 획득에 실패하였습니다")
        return False

    # none || pm-off
    if today_off_info_result.ok() == "none" or today_off_info_result.ok() == "pm-off":
        attendance_result = ApiClient.get_instance().attendance(login_result    .ok().cookies)  # type: ignore

        if attendance_result.is_err():
            print("----Failed : " + current_time + " 출근 실패ㅠㅠㅠㅠ----")
            return False

        else:
            print("----Succeed : " + current_time + " 출근 성공!!----")
            callback_succeed_attendance()
            return True


# 오전 반차
def am_off_attendance(current_time, callback_succeed_attendance):
    login_result = ApiClient.get_instance().login()

    if login_result.is_err():
        logging.error("로그인에 실패하였습니다")
        return False

    today_off_info_result = ApiClient.get_instance().off_check(
        login_result.ok().cookies  # type: ignore
    )

    if today_off_info_result.is_err():
        logging.error("금일 휴가 사용 여부 획득에 실패하였습니다")
        return False

    # am-off
    if today_off_info_result.ok() == "am-off":
        attendance_result = ApiClient.get_instance().attendance(login_result.ok().cookies)  # type: ignore

        if attendance_result.is_err():
            print("----Failed : " + current_time + " 출근 실패ㅠㅠㅠㅠ----")
            return False
        else:
            print("----Succeed : " + current_time + " 출근 성공!!----")
            callback_succeed_attendance()
            return True
