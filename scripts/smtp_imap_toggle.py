import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 웹 드라이버 설정 (Chrome 기준)
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # GUI 없이 실행

driver = webdriver.Chrome(options=options)

EMAIL = os.environ.get('EMAIL')
ID = os.environ.get('ID')
PASSWORD = os.environ.get('PASSWORD')

def login_mailplug():
    driver.get("https://login.mailplug.com/login")

    # 첫 번째 로그인 화면에서 이메일 입력
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login_input"))  # 첫 번째 화면의 이메일 입력 필드 ID
    )
    email_input.clear()
    email_input.send_keys(EMAIL + Keys.RETURN)

    # 다음 페이지로 전환 대기
    WebDriverWait(driver, 10).until(
        EC.url_contains("mailplug.com/member/login")  # URL이 변경될 때까지 대기
    )

    # 두 번째 로그인 화면에서 아이디와 비밀번호 입력
    id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "cid"))  # 아이디 입력 필드
    )
    id_input.clear()
    id_input.send_keys(ID)  # 도메인은 자동 추가

    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "cpw"))  # 비밀번호 입력 필드
    )
    password_input.clear()
    password_input.send_keys(PASSWORD + Keys.RETURN)

    # 로그인 리디렉션 완료 대기 (최종적으로 gw.mailplug.com이 나올 때까지)
    WebDriverWait(driver, 15).until(
        EC.url_contains("gw.mailplug.com")
    )

    print("로그인 완료 및 리디렉션 확인")


def navigate_to_pop3():
    driver.get("https://gw.mailplug.com/mail/setting")
    time.sleep(1)
    pop3_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'POP3/IMAP')]"))
    )
    pop3_button.click()
    WebDriverWait(driver, 10).until(
        EC.url_contains("mail/setting/pop3")
    )
    time.sleep(1)
    print("POP3 설정 페이지로 이동 완료")


def handle_popup():
    try:
        popup_buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='확인']]")
        if popup_buttons:
            for button in popup_buttons:
                driver.execute_script("arguments[0].click();", button)
                print("팝업 닫기 완료")
                time.sleep(1)  # 팝업 닫힌 후 대기
        else:
            print("팝업이 없음, 진행")
    except Exception as e:
        print("팝업이 표시되지 않음 또는 닫기 실패:", str(e))


def navigate_to_imap():
    try:
        handle_popup()  # 불필요한 추가 호출 방지
        imap_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'text-cool-800') and contains(text(), 'IMAP')]"))
        )
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'text-cool-800') and contains(text(), 'IMAP')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", imap_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", imap_button)
        WebDriverWait(driver, 10).until(
            EC.url_contains("mail/setting/imap")
        )
        time.sleep(1)
        print("IMAP 설정 페이지로 이동 완료")
    except Exception as e:
        print("IMAP 버튼 클릭 실패:", str(e))


def toggle_checkbox(checkbox_id, enable=True):
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, checkbox_id))
    )
    current_state = driver.execute_script("return arguments[0].checked;", checkbox)
    if (enable and not current_state) or (not enable and current_state):
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(1)
    print(f"{checkbox_id} 설정 {'활성화' if enable else '비활성화'} 완료")
    handle_popup()


try:
    login_mailplug()
    navigate_to_pop3()
    toggle_checkbox("use_pop3", enable=False)
    time.sleep(1)
    toggle_checkbox("use_pop3", enable=True)
    handle_popup()  # 추가 호출 방지
    navigate_to_imap()
    toggle_checkbox("use_imap", enable=False)
    time.sleep(1)
    toggle_checkbox("use_imap", enable=True)

    print("자동화 완료. 창을 닫으려면 Ctrl+C를 누르세요.")
    while True:
        time.sleep(1)

finally:
    driver.quit()
