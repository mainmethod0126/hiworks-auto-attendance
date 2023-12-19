from datetime import datetime

from target_time_generator import generate_target_times
from attendance_scheduler import attendance_task

import yaml
import threading
import os
import argparse
import sys

# argparse를 사용하여 명령행 인자 파싱
parser = argparse.ArgumentParser(description='Script description')
parser.add_argument('-config', help='Path to the config file')
args = parser.parse_args()



# -config 옵션으로 전달된 값이 있는지 확인하고, 없으면 디폴트 경로 사용
config_path = args.config if args.config else os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config.yml')
    
print("config_path : " + config_path)
    

# config 파일 읽기
with open(config_path, 'r') as config_file:
    config_data = yaml.safe_load(config_file)


none_and_pm_off_target_times = []
am_off_target_times = []

def reset_target_times():
    
    # -----------------------target times 생성--------------------------
    print("start reset target times")
    
    none_and_pm_off_start_time = datetime.strptime(config_data['none_and_pm_off_range']['start_time'], "%H:%M:%S")
    none_and_pm_off_end_time = datetime.strptime(config_data['none_and_pm_off_range']['end_time'], "%H:%M:%S")
    am_off_start_time = datetime.strptime(config_data['am_off_range']['start_time'], "%H:%M:%S")
    am_off_end_time = datetime.strptime(config_data['am_off_range']['end_time'], "%H:%M:%S")
    interval = config_data['interval']
    retry_count = config_data['retry_count']
    
    global none_and_pm_off_target_times
    global am_off_target_times

    none_and_pm_off_target_times = generate_target_times(none_and_pm_off_start_time, none_and_pm_off_end_time, interval, retry_count)
    am_off_target_times = generate_target_times(am_off_start_time, am_off_end_time, interval, retry_count)

    for target_time in none_and_pm_off_target_times:
        print("none_and_pm_off_target_times : " + target_time.strftime("%H:%M:%S"))

    for target_time in am_off_target_times:
        print("am_off_target_times : " + target_time.strftime("%H:%M:%S"))
    

reset_target_times()


# 쓰레드 시작
thread = threading.Thread(target=attendance_task, args=(none_and_pm_off_target_times, am_off_target_times, reset_target_times))
thread.start()

# 스레드가 종료될 때까지 기다림
thread.join()
