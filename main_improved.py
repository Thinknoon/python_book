import requests
from requests.cookies import RequestsCookieJar
import json
import time
import os
import sys
import datetime
import copy

sys_args = int(sys.argv[1])
reverse_data = datetime.datetime.now() + datetime.timedelta(days=6)
reverse_data = reverse_data.strftime('%Y-%m-%d')
reverse_time = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
                "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00"]
time_begin = time.time()
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


if __name__ == '__main__':
    cookies = get_cookies()
    data = add_reverse_data(sys_args)
    data_confirm = copy.copy(data)
    data_confirm.update({"remarks": "wish a better result"})
    while True:
        time_present = time.time()
        session = requests.session()
        if (time_present - time_begin) > 400:
            break
        else:
            pass
        session_reu = session.post(url=url, cookies=cookies, headers=header, data=data_confirm, verify=False)
        print("时间段" + data['beginTime'] + "--" + data['endTime'] + session_reu.text[38:49])
        if "true" in session_reu.text:
            session_confirm = session.post(url=url_confirm, cookies=cookies, headers=header, data=data_confirm, verify=False)
            while not ("true" in session_confirm.text):
               session_confirm = session.post(url=url_confirm, cookies=cookies, headers=header, data=data_confirm, verify=False)
            print("时间段" + data['beginTime'] + "--" + data['endTime'] + session_confirm.text[38:49])
            sys.exit(0)
        else:
            print("时间段" + data['beginTime'] + "--" + data['endTime'] + session_reu.text[38:49])
