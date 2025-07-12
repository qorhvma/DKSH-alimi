from flask import Flask, request, jsonify
import base64
from bs4 import BeautifulSoup
import requests
from time import time
from datetime import date

application = Flask(__name__)


def tagRemove(x):
    """HTML 태그 제거 및 정리"""
    for i in range(len(x)):
        text = str(x[i])
        # HTML 태그 제거
        replacements = [
            ['<p>', ''], ['</p>', ''],
            ['<span>', '('], ['</span>', ')'],
            ['&amp;', '&']
        ]
        for old, new in replacements:
            text = text.replace(old, new)
        x[i] = text


def get_lunch(year: int, month: int, day: int):
    Call_Time = time()

    # 세션 생성 (쿠키 자동 관리)
    session = requests.Session()

    # User-Agent 설정 (브라우저처럼 보이도록)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 \
        Safari/537.36'
    })

    print(f"[{Call_Time}]: 로그인 페이지 접속")
    login_url = "https://dankook.riroschool.kr/ajax.php"
    login_page = session.get(login_url)

    # 로그인 페이지에서 필요한 정보 추출 (CSRF 토큰 등이 있을 수 있음)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    print(f"[{Call_Time}]: 로그인 시도")
    login_data = {
        'app': 'user',
        'mode': 'login',
        'userType': '1',
        'id': 'qorhvmsqorhvma@gmail.com',
        'pw': base64.b64decode(b'YW5nZWwxMDA0Xl4=').decode('utf-8')
    }

    # 로그인 POST 요청
    login_response = session.post(login_url, data=login_data)

    # 로그인 성공 여부 확인
    if "로그인" in login_response.text or login_response.status_code != 200:
        print(f"[{Call_Time}]: 로그인 실패 가능성 - 응답 확인 필요")
    else:
        print(f"[{Call_Time}]: 로그인 성공으로 추정")

    # 급식 페이지 URL 생성
    meal_url = f"https://dankook.riroschool.kr/meal_schedule.php?db=2303&action=day&year={year}&month={month}&day={day}"

    print(f"[{Call_Time}]: 급식 페이지 로드")
    meal_response = session.get(meal_url)

    print(f"[{Call_Time}]: 페이지 파싱")
    soup = BeautifulSoup(meal_response.text, 'html.parser')

    # 메뉴 정보 추출
    menu_elements = soup.select('#container > div > div.renewal_wrap.meal_schedule_wrapper > div.meal_day_contents_wrapper > div > div > div.meal_day_view_middle.meal_view > div.list.meal_day_popup_btn > p')

    # 위험 정보 추출
    danger_elements = soup.select('#container > div > div.renewal_wrap.meal_schedule_wrapper > div.meal_schedule_bottom > p')

    # 메뉴와 위험 정보 정리
    menu = menu_elements.copy()
    danger = danger_elements.copy()

    tagRemove(menu)
    tagRemove(danger)

    # 결과 출력
    response_text = meal_response.text
    wrong = len(response_text) < 116000
    print(f"[{Call_Time}]: wrong:{wrong}")
    print(f"[{Call_Time}]: url:{meal_url}")
    print(f"[{Call_Time}]: Parsing_Result:{menu}")
    print(f"[{Call_Time}]: Danger:{danger}")
    print(f"[{Call_Time}]: 종료")
    return {
        'Call_Time': f'{Call_Time}',
        'url': f'{meal_url}',
        'menu': menu,
        'Danger': danger,
        "wrong": f"{wrong}"
    }

# 웹 페이지
@application.route("/")
def hello():
    return "이 곳에는 아무것도 없습니다!(여기 왜 들어옴)"


# lunch 서버
@application.route("/lunch", methods=['POST'])
def lunch():
    req = request.get_json()
    # if "Interactive_Date" in req["action"]["detailParams"]:
    #     today=date.today.timetuple()
    #     today=[today[0], today[1], today[2]]
    #     interactive_date_req = req["action"]["detailParams"]['Interactive_Date']['value']
    #     date = today
    #     if interactive_date_req == '오늘':
    #         pass
    #     elif interactive_date_req == '어제':
    #         date[2]-=1
    #     elif interactive_date_req == '모레':
    #         date[2]+=2
    #     elif interactive_date_req == '내일':
    #         date[2]+=1
        
    date = req["action"]["detailParams"]["date"]["origin"]
    date = list(map(int, date.split('-')))
    lunch_inf = get_lunch(date[0], date[1], date[2])
    
    requestText = f'{date}\n'
    for food in lunch_inf['menu']:
        requestText += '- '+food+'\n'
    requestText += '참고: '
    requestText += lunch_inf['Danger'][0]

    # 답변 텍스트 설정
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": requestText
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True)
