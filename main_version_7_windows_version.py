# -*- coding: utf-8 -*- 
import execjs
from selenium import webdriver
from selenium.webdriver.firefox import service
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import time
from requests.cookies import RequestsCookieJar
from selenium.webdriver.common.keys import Keys
import json
import os
import sys
import datetime
import requests
import copy
import re
import numpy as np
import imageio
from chaojiying import cjy

#reverse_data = datetime.datetime.now() + datetime.timedelta(days=6)
today = datetime.datetime.now().strftime('%Y-%m-%d')
instrumentId = '1229'
reverse_time = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
        "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30","19:00"]
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Connection": "keep-alive"
}
url = "http://lims.gzzoc.com/account/appointment/BeforeBook"
url_confirm = "http://lims.gzzoc.com/account/appointment/book"
data = {
    "instrumentId": instrumentId,
    "beginTime": "2020-09-20 09:30",
    "endTime": "2020-09-20 10:30"
}
def get_cookies():
    s = Service('./geckodriver.exe')
    driver = webdriver.Firefox(service=s)
    driver.get(f"http://lims.gzzoc.com/account/login?returnurl=%2Fclient%2Finstrument%2Fdetail%2F{instrumentId}")
    # alert = driver.find_element_by_class_name("jconfirm-buttons")
    alert = driver.find_element(By.XPATH, '//div[@class="jconfirm-buttons"]/button[1]' )
    alert.click()
    user_name = driver.find_element(By.NAME,"userName")
    pass_word = driver.find_element(By.ID,"password")
    user_name.clear()
    pass_word.clear()
    user_name.send_keys("30375")
    pass_word.send_keys("Xnn18955246594")
    time.sleep(20)
    with open('cookies.txt', 'w') as cookief:
        cookief.write(json.dumps(driver.get_cookies()))
    driver.close()


def login_by_cookies():
    s = Service('./geckodriver.exe')
    driver = webdriver.Firefox(service=s)
    driver.get(f"http://lims.gzzoc.com/account/login?returnurl=%2Fclient%2Finstrument%2Fdetail%2F{instrumentId}")
    # alert = driver.find_element_by_class_name("jconfirm-buttons") 错误
    alert = driver.find_element(By.XPATH, '//div[@class="jconfirm-buttons"]/button[1]' )
    alert.click()
    driver.delete_all_cookies()
    with open('cookies.txt', 'r') as cookief:
        cookieslist = json.load(cookief)
        for cookie in cookieslist:
            driver.add_cookie(cookie)
    driver.refresh()
    return driver


def check_net_connection():
    print("正在测试与服务器的连接")
    ans = os.system("ping 219.135.135.154")  # 眼科中心的服务器ip是219.135.135.154
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
    args_begin_time = reverse_date + " " + reverse_time[args_index]
    args_end_time = reverse_date + " " + reverse_time[args_index + 4]
    data['beginTime'] = args_begin_time
    data['endTime'] = args_end_time
    return data

def get_reverse_time_index(args_input_time):
    tem_index = args_input_time.split(',')
    tem_reverse_index=[int(i) for i in tem_index]
    return tem_reverse_index

def img_process(args_img):
    black_dot = []
    for i in args_img:
        tem_black_dat = (i < 200)
        black_dot.append(tem_black_dat)
    is_black_dot = black_dot[0]
    for j in black_dot:
        is_black_dot = np.bitwise_and(is_black_dot,j)
    is_black_dot = np.where(is_black_dot==False,255,is_black_dot)
    is_black_dot = np.where(is_black_dot==True,0,is_black_dot)
    is_black_dot = np.uint8(is_black_dot)
    return is_black_dot
    


if __name__ == '__main__':
    print(f'!!!!!!! Attention!!!!! 当前预约的设备是 {instrumentId}')
    print(f'!!!!!!! Attention!!!!! 当前预约的设备是 {instrumentId}')
    print(f'!!!!!!! Attention!!!!! 当前预约的设备是 {instrumentId}')
    reverse_date = input("请输入预约日期，格式为Y-m-d，例如 2020-09-20，务必保证格式正确")
    while not re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}',reverse_date):
        print('日期格式错误，请重新输入')
        reverse_date = input("请输入预约日期，格式为Y-m-d，例如 2020-09-20，务必保证格式正确")
    print("请输入你想要预约的开始时间编号，预约长度为2h")
    print("1代表9:00，2代表9:30，依此类推，最大为16代表17:00")
    input_begin_time = input("请输入预约起始时间：英文逗号隔开，enter结束，你可以输入5个时间编号")
    reverse_time_index = get_reverse_time_index(input_begin_time)
    check_net_connection()
    str_pre_login = "登录注册"
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
    session = requests.session()
    cookies = get_local_cookies()
    session_get = requests.session()
    session_get_rev = session_get.get(f'http://lims.gzzoc.com/client/instrument/detail/{instrumentId}')
    while ("现时段不可进行预约" in session_get_rev.text):
        session_get_rev = session_get.get(f'http://lims.gzzoc.com/client/instrument/detail/{instrumentId}')
        print("尚未到达预约时间，正在等待...")
    for rev_index in reverse_time_index:
        
        # 生成验证码
        var = '''
            function newGuid() {
                function S4() {
                    return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
                }
                return (S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4());
            }
        '''
        data = add_reverse_data( rev_index )
        data_confirm = copy.copy( data )
        while True:
            js_proc = execjs.compile( var )
            codeid = js_proc.call( 'newGuid' )
            imgurl = 'http://lims.gzzoc.com/Account/GetBookSecurityCode?codeid=' + codeid
            img_org = imageio.mimread(imgurl)
            img_pced = img_process(img_org)
            imageio.imwrite('img.gif', img_pced)
            res = cjy( 'img.gif' )['pic_str']
            data_confirm.update({"remarks": "wish a better result",'codeId':codeid,'validCode':res})
            session_reu = session.post(url=url_confirm, cookies=cookies, headers=header, data=data_confirm, verify=False)
            imageio.imwrite(f'./train_datasets/processed/{today}_{res}.gif', img_pced)
            imageio.imwrite(f'./train_datasets/org/{today}_{res}.gif', np.uint8(img_org[0]))
            if "请求处理成功" in session_reu.text:
                print("时间段" + data['beginTime'] + "--" + data['endTime'] + session_reu.text[38:49])
                break
            elif '预约时间与其他用户重叠' in session_reu.text:
                print( "时间段" + data['beginTime'] + "--" + data['endTime'] + session_reu.text[38:49] )
                break
            else:
                print("时间段" + data['beginTime'] + "--" + data['endTime'] + session_reu.text[38:49])
            print('把验证码加入训练集文件夹...')          
    print("预约结束")
