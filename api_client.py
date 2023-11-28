from datetime import datetime
from result import ResultBuilder
from result import Result

import yaml

# config.yml 파일 읽기
with open("config.yml", "r") as config_file:
    config_data = yaml.safe_load(config_file)

import requests
import re


class SingletonError(Exception):
    pass


class ApiClientMeta(type):
    def __new__(cls, name, bases, dct):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, name, bases, dct)
        return cls._instance


class ApiClient:
    _instance = None

    def __init__(self, config_data) -> None:
        if self._instance is not None:
            raise SingletonError(
                "ApiClient is a singleton class. Use get_instance() method to get the instance."
            )
        self.config_data = config_data

    @classmethod
    def get_instance(cls) -> "ApiClient":
        if cls._instance is None: 
            cls._instance = cls(config_data)
        return cls._instance

    # 테스트를 위해서 외부에서 config_data를 주입할 수 있도록 하였습니다.
    # 테스트 이외의 용도로는 사용하지 말아주세요
    def set_config_data(self, config_data):
        self.config_data = config_data

    def login(self) -> Result:
        api_url = self.config_data["login_api"]["url"]
        login_id = self.config_data["login_api"]["id"]
        login_pw = self.config_data["login_api"]["pw"]

        headers = {"Content-Type": "application/json"}
        body = {"id": login_id, "password": login_pw, "ip_security_level": "1"}

        response = requests.post(
            api_url,
            headers=headers,
            json=body,
            verify=self.config_data["use_ssl_verification"],
        )

        if response is None or response.status_code != 200:
            return ResultBuilder.err().build()
        else:
            return ResultBuilder.ok(response).build()

    def off_check(self, cookies) -> Result:
        current_date = datetime.today().strftime("%Y-%m-%d")

        # 금일 근무 정보 가져오기
        work_calendar_api_url = self.config_data["work_calendar_api"]["url"]
        params = {
            "filter[work_date][gte]": current_date,
            "filter[work_date][lte]": current_date,
            "page[limit]": 25,
            "page[offset]": 0,
        }

        today_work_info_response = requests.get(
            work_calendar_api_url,
            params=params,
            cookies=cookies,
            verify=self.config_data["use_ssl_verification"],
        )
        if today_work_info_response is None or today_work_info_response.status_code != 200:
            return ResultBuilder().err("금일 근무 계획 정보를 얻어오지 못했습니다.").build()

        # JSON 형식의 응답을 파이썬 딕셔너리로 변환
        today_work_info = today_work_info_response.json()

        # user_work_data에 접근
        datas = today_work_info["data"]["user_work_data"]

        for data in datas:
            if data["work_date"] == current_date:
                if data["day_off_type"] != 0:  # 주말,공휴일 여부를 확인하기 위함 (주말 또는 공휴일이면 0이 아님)
                    return ResultBuilder().ok("full-off").build()

                if self.config_data[
                    "use_in_progress_approval"
                ]:  # 금일 휴가를 사용했는지를 "진행중인 결재함"에서 확인합니다 (특징 : 휴가 결재가 완료되어있지 않아도 됨)
                    max_number = self.__get_in_progress_approval_max_page_number(
                        cookies
                    ).ok()
                    approval = (
                        self.__get_today_vacation_approval_by_in_progress_approval(
                            cookies, max_number, current_date
                        ).ok()
                    )

                    if approval is not None:
                        html_text = self.__get_view(cookies, approval).ok()

                        if "09:00~14:00" in html_text:
                            return ResultBuilder().ok("am-off").build()
                        elif "14:00~18:00" in html_text:
                            return ResultBuilder().ok("pm-off").build()
                        elif "종일" in html_text:
                            return ResultBuilder().ok("full-off").build()

                if (
                    "vacation_data" not in data
                ):  # 휴가 사용 여부를 "주간 캘린더"에서 확인합니다 (특징 : 휴가 결재가 사전에 완료되어있어야 함)
                    return ResultBuilder().ok("none").build()
                else:  # 휴가 사용 시, 오전반차, 오후반차, 연차 구분
                    for vacation in data["vacation_data"]:
                        if vacation["time_type"] == "H":
                            if vacation["start_time"] == "09:00:00":
                                return ResultBuilder().ok("am-off").build()
                            elif vacation["start_time"] == "14:00:00":
                                return ResultBuilder().ok("pm-off").build()
                        elif vacation["time_type"] == "D":
                            return ResultBuilder().ok("full-off").build()
        return ResultBuilder().err("Invalid work_date").build()

    def attendance(self, cookies) -> Result:
        # -----------------------출근--------------------------
        attendance_api_url = self.config_data["attendance_api"]["url"]

        headers = {"Content-Type": "application/json"}

        body = {"data": {"type": "1"}}

        attendance_response = requests.post(
            attendance_api_url,
            headers=headers,
            json=body,
            cookies=cookies,
            verify=self.config_data["use_ssl_verification"],
        )

        if attendance_response is None:
            return ResultBuilder.err(False).build()

        return (
            ResultBuilder.ok(True).build()
            if attendance_response.status_code == 200
            or attendance_response.status_code == 201
            else ResultBuilder.err(False).build()
        )

    def __get_today_vacation_approval_by_in_progress_approval(
        self, cookies, max_page_number, current_date
    ) -> Result:
        in_progress_approval_api = (
            self.config_data["approval_api"]["base_url"]
            + "/"
            + self.config_data["approval_api"]["sub_url"]["in_progress"]
        )

        date_object = datetime.strptime(current_date, "%Y-%m-%d")

        # yyyy년 mm월 dd일과 같이 한글 형식으로 변환합니다
        date_kor_format = self.__date_to_kor_date_format(date_object)

        for current_page_number in range(1, max_page_number + 1):
            payload = {
                "page": str(current_page_number),
                "pStatus": "P",
                "pMenu": "get_document_list",
            }

            response = requests.post(
                in_progress_approval_api,
                data=payload,
                cookies=cookies,
                verify=self.config_data["use_ssl_verification"],
            )

            if response is None:
                return ResultBuilder.err("result is none").build()

            response_json = response.json()

            for approval in response_json["result"]:
                if (
                    "휴가 신청" in approval["title"]
                    and date_kor_format in approval["title"]
                ):
                    return ResultBuilder.ok(approval).build()

    def __get_view(self, cookies, approval) -> Result:
        approval_no = re.search(r"\d+", approval["link"]).group()

        approval_view_url = (
            self.config_data["approval_api"]["base_url"]
            + "/"
            + "approval/document/view/"
            + approval_no
            + "/condition"
        )

        response = requests.get(
            approval_view_url,
            cookies=cookies,
            verify=self.config_data["use_ssl_verification"],
        )

        if response is None:
            return ResultBuilder.err("result is none").build()
        
        return ResultBuilder.ok(response.text).build()  

    def __get_in_progress_approval_max_page_number(self, cookies) -> Result:
        in_progress_approval_api = (
            self.config_data["approval_api"]["base_url"]
            + "/"
            + self.config_data["approval_api"]["sub_url"]["in_progress"]
        )

        payload = {"pMenu": "get_approval_count"}

        response = requests.post(
            in_progress_approval_api,
            data=payload,
            cookies=cookies,
            verify=self.config_data["use_ssl_verification"],
        )

        if response is None:
            return ResultBuilder.err("result is none").build()

        approval_count = response.json()

        in_progress_approval_count = approval_count["result"]["p"]

        # 한페이지의 리스트 size 는 15가 박혀있는 듯
        table_item_size = 15

        # 페이지는 1부터 시작합니다 그렇기 때문에 + 1합니다
        max_page_number = int((in_progress_approval_count) / table_item_size) + 1

        return ResultBuilder.ok(max_page_number).build()

    def __date_to_kor_date_format(self, date):
        # 날짜 객체에서 년, 월, 일을 추출
        year = date.year
        month = date.month
        day = date.day

        # 변환된 텍스트 반환
        kor_date = f"{year}년 {month}월 {day}일"
        return kor_date
