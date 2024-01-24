from datetime import datetime

from target_time_generator import generate_target_times
from config_module import load_config, get_config_data

import threading
import os
import argparse
import sys

# argparse를 사용하여 명령행 인자 파싱
parser = argparse.ArgumentParser(description="Script description")
parser.add_argument("-config", help="Path to the config file")
args = parser.parse_args()

# -config 옵션으로 전달된 값이 있는지 확인하고, 없으면 디폴트 경로 사용
config_path = (
    args.config
    if args.config
    else os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "config.yml")
)

print("config_path : " + config_path)


# config를 모듈에 로딩
load_config(config_path)

# config 데이터 얻기
config_data = get_config_data()

none_and_pm_off_target_times = []
am_off_target_times = []



# def main():
#     if "-do" in sys.argv:
#         do_attendance()
#     else:
#         print("'-do' 옵션이 없습니다.")

