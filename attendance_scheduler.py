from datetime import datetime
from api_client import ApiClient


import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ApiErrException(Exception):
    pass


def api_err_handler():
    raise ApiErrException("API 호출 결과가 Failed입니다")


def attendance_task(
    none_and_pm_off_target_times, am_off_target_times, callback_succeed_attendance
):
    print("지금부터 출근 스케줄러가 실행됩니다!")
    print("target times 에 출근을 시도하니 해당 시간 이후에 출근 여부 확인해주시길 바랍니다.")

    while True:
        try:
            current_time = datetime.today().strftime("%H:%M:%S")

            is_attended = False

            for target_time in none_and_pm_off_target_times:
                if current_time == target_time.strftime("%H:%M:%S"):
                    login_result = ApiClient.get_instance().login().ok()

                    if login_result.is_err():
                        logging.error("로그인에 실패하였습니다")
                        continue

                    today_off_info_result = ApiClient.get_instance().off_check(
                        login_result.ok().cookies
                    ).ok()

                    if today_off_info_result.is_err():
                        logging.error("금일 휴가 사용 여부 획득에 실패하였습니다")
                        continue

                    # none || pm-off
                    if today_off_info_result.ok() == "none" or today_off_info_result.ok() == "pm-off":
                        attendance_result = ApiClient.get_instance().attendance(login_result.ok().cookies).ok()

                        if attendance_result.is_err():
                            print("----Failed : " + current_time + " 출근 실패ㅠㅠㅠㅠ----")

                        else:
                            print("----Succeed : " + current_time + " 출근 성공!!----")
                            callback_succeed_attendance()
                            is_attended = True
                            break

            if is_attended == False:
                for target_time in am_off_target_times:
                    if current_time == target_time.strftime("%H:%M:%S"):
                    
                        login_result = ApiClient.get_instance().login().ok()

                        if login_result.is_err():
                            logging.error("로그인에 실패하였습니다")
                            continue


                        today_off_info_result = ApiClient.get_instance().off_check(
                            login_result.ok().cookies
                        ).ok()

                        if today_off_info_result.is_err():
                            logging.error("금일 휴가 사용 여부 획득에 실패하였습니다")
                            continue

                        # am-off
                        if today_off_info_result.ok() == "am-off":
                            attendance_result = ApiClient.get_instance().attendance(login_result.ok().cookies).ok()

                            if attendance_result.is_err():
                                print("----Failed : " + current_time + " 출근 실패ㅠㅠㅠㅠ----")

                            else:
                                print("----Succeed : " + current_time + " 출근 성공!!----")
                                callback_succeed_attendance()
                                break
        except Exception as e:
            print("스케줄러 동작 중에 예외가 발생하였으나, 스케줄러는 항상 실행되어야 하기에 익셉션을 방출하지 않고 로그만 기록합니다 " + e)

        time.sleep(1)



