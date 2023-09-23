# hiworks auto attendance

hiworks 로그인 후 휴가 정보를 확인하여 정해진 시간 범위 내에서 "출근" 체크를 자동으로 해줍니다.

> 주의! : 출근을 보조하는 용도이며, 해당 S/W 사용으로 발생하는 불이익에는 S/W 사용자 본인에게 책임이 있음을 알려드립니다. (비정상 동작으로 지각, 또는 Hiworks 계정 정지 등등)

## Reason for production

정상 출근하였으나, 출근 체크를 깜빡하여 지각 처리되는 눈물나는 경우가 종종 발생하여, 출근 기록을 보조하는 용도로 만들었습니다.

## Usage

### config.yml (required)

```yml
login_api:
  url: "https://auth-api.office.hiworks.com/office-web/login"
  id: "test@mycompany.co.kr"
  pw: "test!2345"

work_calendar_api:
  url: "https://hr-work-api.office.hiworks.com/v4/my-work-data-calendar"

attendance_api:
  url: "https://hr-timecheck-api.office.hiworks.com/v4/web/time-record"

approval_api:
  base_url: "https://approval.office.hiworks.com/softcamp.co.kr"
  sub_url:
    in_progress: approval/document_ajax

use_in_progress_approval: true

none_and_pm_off_range:
  start_time: "08:30:00"
  end_time: "08:55:00"
am_off_range:
  start_time: "13:30:00"
  end_time: "13:55:00"
interval: 0
retry_count: 3
```

| **Category**             | **Key**                          | **Description**                                                                                                                      |
| ------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| login_api                | login_api.url                    | hiworks 로그인 api url 입니다.                                                                                                       |
|                          | login_api.id                     | hiworks 로그인 계정 id입니다.                                                                                                        |
|                          | login_api.pw                     | hiworks 로그인 계정 password입니다.                                                                                                  |
| work_calendar_api        | work_calendar_api.url            | hiworks 근무 달력 정보 api url 입니다. 공휴일, 주말, 연차, 반차 등을 구분하기 위해 사용합니다.                                       |
| attendance_api           | attendance_api.url               | 출근 체크 api url 입니다.                                                                                                            |
| none_and_pm_off_range    | none_and_pm_off_range.start_time | "종일 근무 & 오후 반차" 일 경우에 출근을 진행할 시간 범위의 시작 시간입니다.                                                         |
|                          | none_and_pm_off_range.end_time   | "종일 근무 & 오후 반차" 일 경우에 출근을 진행할 시간 범위의 종료 시간입니다.                                                         |
| am_off_range             | am_off_range.start_time          | "오전 반차" 일 경우에 출근을 진행할 시간 범위의 시작 시간입니다.                                                                     |
|                          | am_off_range.end_time            | "오전 반차" 일 경우에 출근을 진행할 시간 범위의 종료 시간입니다.                                                                     |
| interval                 | interval                         | 출근을 시도하는 주기 입니다. `0` 으로 셋팅할 경우 start_time, end_time 범위에서 랜덤하게 시간을 지정하여 출근을 시도합니다. (분단위) |
| retry_count              | retry_count                      | 출근 시도 실패 시 최대 재시도 횟수 입니다. 이전 실패 후 interval 값만큼의 시간(분)이 지난 후 재시도합니다.                           |
| approval_api             | approval_api.base_url            | 전자결재 api 의 base url 입니다                                                                                                      |
|                          | approval_api.sub_url             | 전자결재 api 의 하위 도메인 url 입니다                                                                                               |
|                          | approval_api.sub_url.in_progress | 전자결재 api 의 "진행중인 전자결재" 하위 도메인 url 입니다                                                                           |
| use_in_progress_approval | use_in_progress_approval         | 휴가 당일이 되었는데 휴가 결재가 완료되지 않았을 때 휴가 결재를 상신한 내역만으로 오늘을 휴가로 판단할지 여부입니다                  |

### Build

#### pip upgrade

pip 를 최신으로 유지해주시길 바랍니다.

```bash
pip install --upgrade pip
```

#### install dependencies

```bash
pip install requests
pip install pyyaml
```

#### To .exe

##### install pyinstaller

`pip install pyinstaller`

##### do build

`pyinstaller hiworks_auto_attendance.py`

##### artifacts path

`<project dir>/dist`

### execute

1. `config.yml` 파일을 `<project dir>/dist/hiworks auto attendance` 에 생성합니다. 파일 양식을 상단 `config.yml` 항목을 참고해주시면 감사하겠습니다.
2. `<project dir>/dist/hiworks auto attendance/hiworks_auto_attendance.exe` 를 실행합니다
3. 표준 출력으로 `지금부터 출근 스케줄러가 실행됩니다! target times 에 출근을 시도하니 해당 시간 이후에 출근 여부 확인해주시길 바랍니다` 라는 텍스트가 뜨면 정상적으로 가동

- **출근 성공시 표준 출력 :** `----Succeed : <Datetime> 출근 성공!!----`
- **출근 실패시 표준 출력 :** `----Failed : <Datetime> 출근 실패ㅠㅠㅠㅠ!!----`
