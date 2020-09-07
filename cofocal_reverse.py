from selenium import webdriver
import time
import pytesseract
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from PIL import Image
import json
import os
import sys

input_begin_time = "2020-09-10 14:00"
input_end_time = "2020-09-10 16:00"

def get_cookies():
    driver = webdriver.Firefox()
    driver.get("http://lims.gzzoc.com/account/login?returnurl=%2Fclient%2Finstrument%2Fdetail%2F1096")
    alert = driver.find_element_by_class_name("jconfirm-buttons")
    alert.click()
    user_name = driver.find_element_by_id("userName")
    pass_word = driver.find_element_by_id("password")
    user_name.clear()
    pass_word.clear()
    user_name.send_keys("17827065668")
    pass_word.send_keys("123456")
    time.sleep(20)
    with open('cookies.txt', 'w') as cookief:
        cookief.write(json.dumps(driver.get_cookies()))
        driver.close()


def login_by_cookies():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
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
    except NoSuchElementException as e:
        return False
    else:
        return True


def check_net_connection():
    print("正在测试与服务器的连接")
    ans = os.system("ping 219.135.135.154")  # 眼科中心的服务器ip是219.135.135.154
    if ans == 1:
        print('网络未连接，请重试')
        sys.exit(1)
    else:
        print("网络已连接，尝试登录...")


def confocal_reservation(args_driver_object, args_begin_time, args_end_time):
    begin_time = args_driver_object.find_element_by_id("beginTime")
    end_time = args_driver_object.find_element_by_id("endTime")
    args_driver_object.execute_script('arguments[0].value= arguments[1]', begin_time, args_begin_time)
    args_driver_object.execute_script('arguments[0].value=arguments[1]', end_time, args_end_time)
    submit_button = args_driver_object.find_element_by_xpath("//button[contains(text(),'预约')]")
    submit_button.click()
    confirm_button = args_driver_object.find_element_by_xpath("//button[contains(text(),'确认')]")
    text = args_driver_object.find_element_by_xpath("//div [contains(@id,'jconfirm')]/div").text
    if "预约成功" in text:
        print("预约成功了")
        sys.exit()
    else:
        print("预约出现问题:" + text)
    confirm_button.click()
    # msg_alert = webdriver_object.switch_to.alert,本网页不是alert的弹窗，而是js自控地div，只能自己定位，并且点击
    # msg_alert.accept()

    # begin_time.send_keys(input_begin_time)
    # end_time.send_keys(input_end_time)#通过js获得数据格式为"2020-08-20 19:30"
    # end_time.send_keys(Keys.ENTER)


if __name__ == '__main__':
    print("时间格式务必正确：例如：2020-08-21 17：30")
    #input_begin_time = input("请输入预约起始时间：")
    #input_end_time = input("请输入预约结束时间：")
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
    print("已经重定向到共聚焦预约页面，正在预约...")
    begin_time_exist = judge_element_exist('beginTime', driver_object)
    end_time_exist = judge_element_exist('endTime', driver_object)
    while not (begin_time_exist & end_time_exist):
        print('尚未到达预约时间，正在等待...')
        driver_object.refresh()
        begin_time_exist = judge_element_exist('beginTime', driver_object)
        end_time_exist = judge_element_exist('endTime', driver_object)
    while True:
        try:
            confocal_reservation(driver_object, input_begin_time, input_end_time)
            print("目前预约的时间为"+input_begin_time+'-'+input_end_time)
        except NoSuchElementException as e:
            print('刷新过快，正在重启任务')
        driver_object.refresh()
        time.sleep(1)
    driver_object.close()
    print("预约结束")
