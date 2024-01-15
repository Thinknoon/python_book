import ddddocr
import time
import requests
import re
import datetime
import sys
import json
import random
# choose which instrument to book
remarks = ""

request_validation_re = re.compile(r'<input name="__RequestVerificationToken" type="hidden" value="([^"]*)" />')
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Connection": "keep-alive"
}

url_confirm = "http://lims.gzzoc.com/account/appointment/book"
login_url = 'https://lims.gzzoc.com/account/Loginnow'


def new_guid(): 
    random_hex = lambda: hex(int((1 + random.random()) * 0x10000))[3:]
    return (
        random_hex() + random_hex() + "-" + random_hex() + "-" + random_hex() + "-" +
        random_hex() + "-" + random_hex() + random_hex() + random_hex()
    )
def wait_to_59min_52sec():
    current_time = datetime.datetime.now()
    target_time = datetime.datetime(current_time.year, current_time.month, current_time.day, 9, 59, 52)
    time_to_wait = target_time - current_time
    if time_to_wait <= datetime.timedelta():
        print("Already 9:59:52")
        return
    print("Waiting for 9:59:52")
    time.sleep(time_to_wait.total_seconds())
    print("Executing code at 9:59:55")

if __name__ == '__main__':
    wait_to_59min_52sec()
    # load book info from book_data.json
    with open('./book_data.json','r') as file:
        book_info = json.load(file)
    if book_info.get('booked') == "true":
        print("current session have been booked")
        sys.exit(0)
    book_info['booked'] = "true"
    with open('./book_data.json','w') as file:
        json.dump(book_info, file)
    # generate a codeid and bind it to server for logging purposes
    safecodeid = new_guid()
    safecode_url = 'http://lims.gzzoc.com/Account/SecurityCode?codeid='+ safecodeid
    session_get_safecode = requests.session()
    safecode_response = session_get_safecode.get(safecode_url,headers=header,stream=True)
    with open('SecurityCode.jpg', 'wb') as file:
            file.write(safecode_response.content)
    ocr = ddddocr.DdddOcr()
    with open('SecurityCode.jpg', 'rb') as f:
        image_bytes = f.read()
    res = ocr.classification(image_bytes)
    print(res)
    login_data = {"wechatId": "","realName": "","gzzocUserNo": "","cellphone": "","isGzzocUserNo": "true","userName": "15616238718",
    "password": "7C547996C074C5E2778C4D9339D6FDC4972D749938284E0E7A588CFBD4922CE2","smsCode": "","code": res,"freeLogin": "true","codeId":safecodeid }
    login_response = session_get_safecode.post(login_url,headers=header,data=login_data)
    if login_response.status_code == 200:
        print('login successful')
    else:
        print(f'login failed and the request response code is {login_response.status_code}')
    # generate book request
    session_get_book = requests.session()
    instrumentId = book_info["instrumentId"]
    session_get_rev = session_get_book.get(f'http://lims.gzzoc.com/client/instrument/detail/{instrumentId}',headers=header,cookies=login_response.cookies)
    codeid_book = new_guid()
    sessionToken = request_validation_re.findall(session_get_rev.text)
    # create a new book rquest info 
    data_confirm = dict()
    data_confirm['instrumentId']=book_info["instrumentId"]
    data_confirm['beginTime']= book_info["beginTime"]
    data_confirm['endTime']= book_info["endTime"]
    data_confirm['remarks']=remarks
    data_confirm['codeId'] = safecodeid
    data_confirm['validCode'] = sessionToken
    data_confirm['__RequestVerificationToken']=sessionToken

    # waitting until the book start
    session_get = requests.session()
    session_get_rev = session_get.get(f'http://lims.gzzoc.com/client/instrument/detail/{instrumentId}')
    while ("现时段不可进行预约" in session_get_rev.text):
        session_get_rev = session_get.get(f'http://lims.gzzoc.com/client/instrument/detail/{instrumentId}')
        print("尚未到达预约时间，正在等待...")
    time.sleep(2)
    session_reu = session_get_book.post(url=url_confirm, cookies=login_response.cookies, headers=header, data=data_confirm, verify=False)
    if session_reu.status_code ==200:
        if "请求处理成功" in session_reu.text:
            print("时间段" + data_confirm['beginTime'] + "--" + data_confirm['endTime'] + session_reu.text[38:])
        elif '预约时间与其他用户重叠' in session_reu.text:
            print( "时间段" + data_confirm['beginTime'] + "--" + data_confirm['endTime'] + session_reu.text[38:])
        else:
            print("时间段" + data_confirm['beginTime'] + "--" + data_confirm['endTime'] + session_reu.text[38:])
    else:
        print(f'服务器拒绝了你的请求,request status code  = {session_reu.status_code}')
