from datetime import datetime

from target_time_generator import generate_target_times
from attendance_scheduler import attendance_task

import yaml
import threading



# config.yml 파일 읽기
with open('config.yml', 'r') as config_file:
    config_data = yaml.safe_load(config_file)


# -----------------------target times 생성--------------------------

none_and_pm_off_start_time = datetime.strptime(config_data['none_and_pm_off_range']['start_time'], "%H:%M:%S")
none_and_pm_off_end_time = datetime.strptime(config_data['none_and_pm_off_range']['end_time'], "%H:%M:%S")
am_off_start_time = datetime.strptime(config_data['am_off_range']['start_time'], "%H:%M:%S")
am_off_end_time = datetime.strptime(config_data['am_off_range']['end_time'], "%H:%M:%S")
interval = config_data['interval']
retry_count = config_data['retry_count']


none_and_pm_off_target_times = generate_target_times(none_and_pm_off_start_time, none_and_pm_off_end_time, interval, retry_count)
am_off_target_times = generate_target_times(am_off_start_time, am_off_end_time, interval, retry_count)

for target_time in none_and_pm_off_target_times:
    print("none_and_pm_off_target_times : " + target_time.strftime("%H:%M:%S"))

for target_time in am_off_target_times:
    print("am_off_target_times : " + target_time.strftime("%H:%M:%S"))




# 쓰레드 시작
thread = threading.Thread(target=attendance_task, args=(none_and_pm_off_target_times, am_off_target_times, config_data))
thread.start()

# 스레드가 종료될 때까지 기다림
thread.join()
