from unittest import mock

import requests

from config_module import load_config, get_config_data


from api_client import ApiClient
from attendance_scheduler import do_attendance
from datetime import datetime

login_id = "aaaa@softcamp.co.kr"
login_pw = "aaaa123!@#"


def test_get_config_data():
    config_path = 'config.yml'
    
    # config를 모듈에 로딩
    load_config(config_path)

    # config 데이터 얻기
    return get_config_data()


def test_login_given_unregistered_account_when_login_request_then_result_is_err_true():

    """
    미등록된 계정으로 하이웍스 로그인 시 로그인 실패합니다.
    """
    config_data = test_get_config_data()

    
    config_data["login_api"]["id"] = 'aaaa'
    config_data["login_api"]["pw"] = 'bbbb'

    ApiClient.get_instance().set_config_data(config_data)

    login_result = ApiClient.get_instance().login()

    assert login_result.is_err() is True

def test_off_check_given_registered_account_when_off_check_request_then_result_is_err_false():
    """
    등록된 계정으로 오늘의 휴가 정보를 획득할 때 획득에 성공합니다
    """
    config_data = test_get_config_data()
    
    config_data["login_api"]["id"] = login_id
    config_data["login_api"]["pw"] = login_pw

    ApiClient.get_instance().set_config_data(config_data)

    login_result = ApiClient.get_instance().login()

    today_off_info_result = ApiClient.get_instance().off_check(
        login_result.ok().cookies # type: ignore
    )

    assert today_off_info_result.is_err() is False
    assert today_off_info_result.ok() is not None


def test_attendance_given_login_false_when_attendance_then_not_throw_exception():
    """
    로그인 실패 시 출근 로직에서 익셉션이 발생하지 않습니다
    """
    config_data = test_get_config_data()
    
    # given
    config_data["login_api"]["id"] = login_id
    config_data["login_api"]["pw"] = login_pw

    ApiClient.get_instance().set_config_data(config_data)

    test_none_and_pm_off_target_times = []
    test_none_and_pm_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))
    
    test_am_off_target_times = []
    test_am_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))

    # 하이웍스 로그인 api가 실패했다고 가정합니다.
    def mock_post(*args, **kwargs):
        if args[0] == config_data["login_api"]["url"]:
            mock_response = mock.Mock()
            mock_response.status_code = 999
            return mock_response
        else:
            # 해당 request가 mock대상이 아닌 것으로 확인되어 원본 request를 그대로 호출합니다.
            return requests.post(*args, **kwargs)

    
    with mock.patch('requests.post', side_effect=mock_post):
        mock_response = mock.Mock()
        mock_post.return_value = mock_response

        # when
        do_attendance(
                test_none_and_pm_off_target_times, test_am_off_target_times, on_success
        )


def test_attendance_given_today_work_info_response_false_when_attendance_then_not_throw_exception():
    """
    금일 출근 정보 조회 실패 시 출근 로직에서 익셉션이 발생하지 않습니다
    """
    
    config_data = test_get_config_data()
    
    # given
    config_data["login_api"]["id"] = login_id
    config_data["login_api"]["pw"] = login_pw

    ApiClient.get_instance().set_config_data(config_data)

    test_none_and_pm_off_target_times = []
    test_none_and_pm_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))
    
    test_am_off_target_times = []
    test_am_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))

    # 금일 근무 정보 조회 api 가 실패했다고 가정합니다.
    def mock_get(*args, **kwargs):
        if args[0] == config_data["work_calendar_api"]["url"]:
            mock_response = mock.Mock()
            mock_response.status_code = 999
            return mock_response
        else:
            # 해당 request가 mock대상이 아닌 것으로 확인되어 원본 request를 그대로 호출합니다.
            return requests.get(*args, **kwargs)

    
    with mock.patch('requests.get', side_effect=mock_get):

        mock_response = mock.Mock()
        mock_get.return_value = mock_response

        # when
        do_attendance(
                test_none_and_pm_off_target_times, test_am_off_target_times, on_success
        )


def test_attendance_given_get_in_progress_approval_max_page_number_response_false_when_attendance_then_not_throw_exception():
    """
    결재 진행중인 휴가 신청서 리스트의 끝 페이지 넘버 조회 실패 시 출근 로직에서 익셉션이 발생하지 않습니다
    """
    
    config_data = test_get_config_data()
    
    # given
    config_data["login_api"]["id"] = login_id
    config_data["login_api"]["pw"] = login_pw

    ApiClient.get_instance().set_config_data(config_data)

    test_none_and_pm_off_target_times = []
    test_none_and_pm_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))
    
    test_am_off_target_times = []
    test_am_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))


    # 결재가 아직 진행중인 휴가 신청서 목록 조회 api 가 실패했다고 가정합니다.
    # 
    def mock_post(*args, **kwargs):
        if args[0] == (
        config_data["approval_api"]["base_url"]
        + "/"
        + config_data["approval_api"]["sub_url"]["in_progress"]
    ) and kwargs.get('data') == {"pMenu": "get_approval_count"}:
            mock_response = mock.Mock()
            mock_response.status_code = 999
            return mock_response
        else:
            # 해당 request가 mock대상이 아닌 것으로 확인되어 원본 request를 그대로 호출합니다.
            return original_requests_post(*args, **kwargs)

    original_requests_post = requests.post

    with mock.patch('requests.post', side_effect=mock_post):

        mock_response = mock.Mock()
        mock_post.return_value = mock_response

        # when
        do_attendance(
                test_none_and_pm_off_target_times, test_am_off_target_times, on_success
        )


def test_attendance_given_get_in_progress_approval_response_false_when_attendance_then_not_throw_exception():
    """
    결재 진행중인 휴가 신청서 조회 실패 시 출근 로직에서 익셉션이 발생하지 않습니다
    """
    
    config_data = test_get_config_data()
    
    # given
    config_data["login_api"]["id"] = login_id
    config_data["login_api"]["pw"] = login_pw

    ApiClient.get_instance().set_config_data(config_data)

    test_none_and_pm_off_target_times = []
    test_none_and_pm_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))
    
    test_am_off_target_times = []
    test_am_off_target_times.append(datetime.strptime(datetime.today().strftime("%H:%M:%S"), "%H:%M:%S"))


    # 결재가 아직 진행중인 휴가 신청서 목록 조회 api 가 실패했다고 가정합니다.
    def mock_post(*args, **kwargs):
        if args[0] == (
        config_data["approval_api"]["base_url"]
        + "/"
        + config_data["approval_api"]["sub_url"]["in_progress"]
    ) and (kwargs.get('data') != {"pMenu": "get_approval_count"}):
            mock_response = mock.Mock()
            mock_response.status_code = 999
            return mock_response
        else:
            # 해당 request가 mock대상이 아닌 것으로 확인되어 원본 request를 그대로 호출합니다.
            return original_requests_post(*args, **kwargs)

    original_requests_post = requests.post

    with mock.patch('requests.post', side_effect=mock_post):

        mock_response = mock.Mock()
        mock_post.return_value = mock_response

        # when
        do_attendance(
                test_none_and_pm_off_target_times, test_am_off_target_times, on_success
        )


def on_success():
    print("출근 성공!!")