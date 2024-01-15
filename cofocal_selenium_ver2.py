from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from urllib import request
import requests
import numpy as np
import time
from datetime import datetime
import re
 

# define what you want to appoint
instrumentId = 26762
appointment_date ='2024-01-19'
# appointment_time 的编码如下：00:00-00:30为1，每30min加1，依次类推... 
appointment_time=[5,6]

def get_login(driver,val_code):
    driver.find_element(By.XPATH,"//input[@id='userName']").send_keys('15616238718')
    driver.find_element(By.XPATH,"//input[@id='password']").send_keys('w1993s03t12c=-')
    driver.find_element(By.XPATH,"//input[@id='validate-code']").send_keys(val_code)
    driver.find_element(By.XPATH,"//button[@type='submit']").click()
    sleep(2)
    return driver

def Fill_time(driver,appointment_date,appointment_time):
    current_appointment_date_period = driver.find_element(By.XPATH,"//div[@id='home']/div/p/b").text
    current_appointment_date = current_appointment_date_period.split('~')[0] 
    current_appointment_date = current_appointment_date.strip()
    start_datetime = datetime.strptime(current_appointment_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(appointment_date, "%Y-%m-%d")
    delta = end_datetime - start_datetime
    if delta.days > 6:
        driver.find_element(By.XPATH,"//a[contains(text(),'下周>>')]").click()
        days = delta.days -5 
    else:
        days = delta.days + 2
    for i in appointment_time:
        driver.find_element(By.XPATH,f"//div[@id='home']/div/div/table/tbody/tr[{i}]/td[{days}]/i").click()
    driver.find_element(By.XPATH,"//button[contains(.,'预约')]").click()
    return driver

def get_tracks(distance):
    v = 0
    m = 20
    tracks = []
    current = 0
    mid = distance*4/5
    while current <= distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        s = v0*m+0.5*a*(m**2)
        current += s
        tracks.append(round(s))
        v = v0+a*m
    return tracks

def get_tracks_Uniform(distance):
    v=25
    tracks=[]
    current=0
    while current+v < distance:
        tracks.append(v)
        current+=v
    tracks.append(distance-current)
    return tracks

def quick_track(distance):
    return [0,20,distance-20]

def extract_numbers(string):
    numbers = re.findall(r'\d+', string)
    return numbers[0]

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument('--ignore-certificate-errors-spki-list')
driver = webdriver.Firefox(options=firefox_options,keep_alive=True)
url = 'https://lims.gzzoc.com/Account/login'
driver.get(url)
driver.maximize_window()
driver.find_element(By.XPATH, '//div[@class="jconfirm-buttons"]/button[1]' ).click()
val_code = input('Enter validate code here:')
val_code = str(val_code)
driver = get_login(driver=driver,val_code=val_code)
session = requests.session()
session_get = requests.session()
session_get_rev = session_get.get(f'http://lims.gzzoc.com/client/instrument/detail/{instrumentId}')
while ("现时段不可进行预约" in session_get_rev.text):
    session_get_rev = session_get.get(f'http://lims.gzzoc.com/client/instrument/detail/{instrumentId}')
    print("尚未到达预约时间，正在等待...")
driver.get(f'https://lims.gzzoc.com/client/instrument/detail/{instrumentId}')
sleep(1)
try:
    driver.find_element(By.XPATH,"//button[contains(.,'确认已读须知')]").click()  
except:
    print('no alert, go on...')
# fill the time
driver = Fill_time(driver=driver,appointment_date=appointment_date,appointment_time=appointment_time)
# obtian distance
sleep(1)
bk_pic= driver.find_element(By.XPATH,"(//div[@class='puzzle-lost-box'])[2]")
distance_str = bk_pic.get_attribute('style')
distance_str = distance_str.split(';')[-3]
distance = int(extract_numbers(distance_str))
tracks = get_tracks_Uniform(distance)
# tracks.append(-(sum(tracks)-distance)) when you using get_tracks,add this 
slice_mouse = driver.find_element(By.XPATH,"//div[@id='huakuai']/div[2]")
ActionChains(driver).click_and_hold(on_element=slice_mouse).perform()
for track in tracks:
    ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
sleep(0.5)
ActionChains(driver).release(on_element=slice_mouse).perform()
driver.find_element(By.XPATH,"//button[contains(.,'确认')]").click()