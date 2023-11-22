import pytest
import yaml

from api_client import ApiClient




def get_config_data():
    with open("C:\\Projects\\hiworks-auto-attendance\\test\\test_config.yml", "r") as config_file:
        return yaml.safe_load(config_file)

@pytest.mark.describe("등록되지 않은 계정으로 로그인을 시도하면 result.is_err의 결과가 true로 나옵니다")
def test_login_given_unregistered_account_when_login_request_then_result_is_err_true():
    config_data = get_config_data()

    login_id = "aaaa@softcamp.co.kr"
    login_pw = "aaaa123!@#"

    config_data["login_api"]["id"] = login_id
    config_data["login_api"]["pw"] = login_pw

    ApiClient.get_instance().set_config_data(config_data)

    login_result = ApiClient.get_instance().login()

    assert login_result.is_err() is True

@pytest.mark.describe("등록된 계정으로 금일 출근 정보를 얻어올 수 있습니다")
def test_off_check_given_registered_account_when_off_check_request_then_result_is_err_false():
    config_data = get_config_data()


    login_id = "aaaa@softcamp.co.kr"
    login_pw = "aaaa123!@#"

    config_data["login_api"]["id"] = login_id
    config_data["login_api"]["pw"] = login_pw

    ApiClient.get_instance().set_config_data(config_data)

    login_result = ApiClient.get_instance().login()

    if login_result.is_err():
        print("하이웍스 로그인에 실패하였습니다")
        return

    today_off_info_result = ApiClient.get_instance().off_check(
        login_result.ok().cookies
    )

    assert today_off_info_result.is_err() is False
    assert today_off_info_result.ok() is not None

