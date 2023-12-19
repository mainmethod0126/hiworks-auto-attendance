
import yaml

# 초기값 설정
config_data = {}

def load_config(config_path):
    global config_data
    with open(config_path, 'r') as config_file:
        config_data = yaml.safe_load(config_file)

def get_config_data():
    global config_data
    return config_data