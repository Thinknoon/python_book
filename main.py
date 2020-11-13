from selenium import webdriver
import time
from requests.cookies import RequestsCookieJar
from selenium.webdriver.common.keys import Keys
import json
import os
import sys
import random
import datetime
import requests
import copy

reverse_data = datetime.datetime.now() + datetime.timedelta(days=6)
reverse_data = reverse_data.strftime('%Y-%m-%d')
reverse_time = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
        "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30","19:00"]
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Connection": "keep-alive"
}
url = "http://lims.gzzoc.com/account/appointment/BeforeBook"
url_confirm = "http://lims.gzzoc.com/account/appointment/book"
data = {
    "instrumentId": "1096",
    "beginTime": "2020-09-20 09:30",
    "endTime": "2020-09-20 10:30"
}
def get_cookies():
    driver = webdriver.Firefox(executable_path='./geckodriver')
    driver.get("http://lims.gzzoc.com/account/login?returnurl=%2Fclient%2Finstrument%2Fdetail%2F1096")
    alert = driver.find_element_by_class_name("jconfirm-buttons")
    alert.click()
    user_name = driver.find_element_by_id("userName")
    pass_word = driver.find_element_by_id("password")
    user_name.clear()
    pass_word.clear()
    user_name.send_keys("12056")
    pass_word.send_keys("18933938220sx")
    time.sleep(20)
    with open('cookies.txt', 'w') as cookief:
        cookief.write(json.dumps(driver.get_cookies()))
    driver.close()


def login_by_cookies():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path='./geckodriver',options=options)
    driver.get("http://lims.gzzoc.com/account/login?returnurl=%2Fclient%2Finstrument%2Fdetail%2F1096")
    alert = driver.find_element_by_class_name("jconfirm-buttons")
    alert.click()
    driver.delete_all_cookies()
    with open('cookies.txt', 'r') as cookief:
        cookieslist = json.load(cookief)
        for cookie in cookieslist:
            driver.add_cookie(cookie)
    driver.refresh()
    return driver


def judge_element_exist(args_str, args_driver_object):
    try:
        args_driver_object.find_element_by_id(args_str)
    except Exception:
        return False
    else:
        return True


def check_net_connection():
    print("正在测试与服务器的连接")
    ans = os.system("ping -c 2 219.135.135.154")  # 眼科中心的服务器ip是219.135.135.154
    if ans == 1:
        print('网络未连接，请重试')
        sys.exit(1)
    else:
        print("网络已连接，尝试登录...")

def get_local_cookies():
    cookiejar = RequestsCookieJar()
    with open("./cookies.txt", "r") as f:
        cookies = json.loads(f.read())
        for cookie in cookies:
            cookiejar.set(cookie['name'], cookie['value'])
    return cookiejar


def add_reverse_data(args_index):
    args_begin_time = reverse_data + " " + reverse_time[args_index]
    args_end_time = reverse_data + " " + reverse_time[args_index + 4]
    data['beginTime'] = args_begin_time
    data['endTime'] = args_end_time
    return data

def get_reverse_time_index(args_input_time):
    tem_index = args_input_time.split(',')
    tem_reverse_index=[int(i) for i in tem_index]
    return tem_reverse_index


if __name__ == '__main__':
    print("请输入你想要预约的开始时间编号，预约长度为2h")
    print("1代表9:00，2代表9:30，依此类推，最大为16代表17:00")
    input_begin_time = input("请输入预约起始时间：英文逗号隔开，enter结束，你可以输入5个时间编号")
    reverse_time_index = get_reverse_time_index(input_begin_time)
    check_net_connection()
    str_pre_login = "登录注册"
    str_confocal = "激光共聚焦显微镜"
    if os.path.exists("cookies.txt"):
        pass
    else:
        get_cookies()
    while True:
        driver_object = login_by_cookies()
        if str_pre_login in driver_object.title:
            print("cookies过期，请在浏览器中手动登录...")
            driver_object.close()
            get_cookies()
        else:
            print("登录成功，正在重定向到共聚焦预约...")
            break

    while not (str_confocal in driver_object.title):
        driver_object.get("http://lims.gzzoc.com/client/instrument/detail/1096")
        print("正在重定向尝试")
    print("已经重定向到共聚焦预约页面，正在预约...")
    begin_time_exist = judge_element_exist('beginTime', driver_object)
    end_time_exist = judge_element_exist('endTime', driver_object)

    while not (begin_time_exist & end_time_exist):
        print('尚未到达预约时间，正在等待...')
        driver_object.refresh()
        begin_time_exist = judge_element_exist('beginTime', driver_object)
        end_time_exist = judge_element_exist('endTime', driver_object)
    driver_object.close()
    session = requests.session()
    cookies = get_local_cookies()
    for rev_index in reverse_time_index:
        data = add_reverse_data(rev_index)
        data_confirm = copy.copy(data)
        data_confirm.update({"remarks": "wish a better result"})
        session_reu = session.post(url=url_confirm, cookies=cookies, headers=header, data=data_confirm, verify=False)
        if "请求处理成功" in session_reu.text:
            print("时间段" + data['beginTime'] + "--" + data['endTime'] + session_reu.text[38:49])
            break
        else:
            pass
        print("时间段" + data['beginTime'] + "--" + data['endTime'] + session_reu.text[38:49])
    print("预约结束")
    sys.exit
