from apscheduler.schedulers.background import BackgroundScheduler

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


class ApiErrException(Exception):
    pass


def api_err_handler():
    raise ApiErrException("API 호출 결과가 Failed입니다")


def reset_scheduler():
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


def run(none_and_pm_off_target_times, am_off_target_times, callback_succeed_attendance):
    # 스케줄러 초기화
    scheduler = BackgroundScheduler()

    for target_time in none_and_pm_off_target_times:
        scheduler.add_job(
            attendance_task,
            "date",
            run_date=target_time,
            id=target_time.strftime("%H:%M:%S"),
        )

    for target_time in am_off_target_times:
        print(target_time)

    scheduler.start()


def attendance_task(
    none_and_pm_off_target_times, am_off_target_times, callback_succeed_attendance
):
    print("지금부터 출근 스케줄러가 실행됩니다!")
    print("target times 에 출근을 시도하니 해당 시간 이후에 출근 여부 확인해주시길 바랍니다.")


# def do_attendance(
#     callback_succeed_attendance
# ):
#     try:


#         is_attended = False

#         if is_attended == False:

#     except Exception as e:
#         print("스케줄러 동작 중에 예외가 발생하였으나, 스케줄러는 항상 실행되어야 하기에 익셉션을 방출하지 않고 로그만 기록합니다 " + e)  # type: ignore


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
        attendance_result = ApiClient.get_instance().attendance(login_result.ok().cookies)  # type: ignore

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
