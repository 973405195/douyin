import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import json
from selenium.webdriver.chrome.service import Service
import http.cookies
import random



def cookies_string_to_dict(cookie_string):
    cookies = http.cookies.SimpleCookie()
    cookies.load(cookie_string)
    cookie_dict = {}
    for key, morsel in cookies.items():
        cookie_dict[key] = morsel.value
    # print(cookie_dict)
    return cookie_dict
# num = 0
suiji_cookies = []
sec_user_ids = []
with open('D:\dyprj\dy_cookie.txt', 'r') as f:
    for line in f:
        cookie_ = line.split('\n')[0]
        suiji_cookies.append(cookie_)
        # 初始化webdriver

author_url = requests.get('https://zt.juzhun.com/admin/authorApi/getList')
author_data = author_url.json()
data = author_data['data']

service = Service(r'C:\Users\李亚航\AppData\Local\Programs\Python\Python37-32\chromedriver.exe')
driver = webdriver.Chrome(service=service)
# print('打开浏览器')
# 打开抖音登录页面
driver.get(f'https://www.douyin.com/')

cookie_num = random.randint(0,len(suiji_cookies)-1)
print(f"账号：{cookie_num}")
# 通过cookies登录
cookies_ = cookies_string_to_dict(suiji_cookies[cookie_num])

for cookie in cookies_:
    # print(cookie,cookies_[cookie])
    driver.add_cookie(
        {
            'domain': '.douyin.com',
            'name': cookie,
            'value': cookies_[cookie],
            'path': '/',
            'expires': None
        }
    )

sleep(5)
# 刷新页面以便cookies生效
driver.refresh()

# 等待页面加载完成
try:
    wait = WebDriverWait(driver, 10)
    login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.douyin-login__header')))
except:
    for author_ in range(0,len(data)):
        # if data[author_]['iconUrl']!=None:
        #     continue
        try:
            ceshi = data[author_]['authorUrl'].split('/')
            sec_user_id = ceshi[len(ceshi) - 1]
            sec_user_ids.append(sec_user_id)
            print(sec_user_id)
            driver.get(f'https://www.douyin.com/user/{sec_user_id}')
            sleep(4)
            name = driver.find_element(By.XPATH,'//h1[@class="GMEdHsXq"]').text
            ico_img = driver.find_element(By.XPATH, '//div[@class="yzJGz3HB"]//img') #头像地址
            guanzhu = driver.find_element(By.XPATH,'//div[@class="Q1A_pjwq ELUP9h2u"][1]/div[2]').text #关注
            fensi = driver.find_element(By.XPATH,'//div[@class="Q1A_pjwq ELUP9h2u"][2]/div[2]').text
            digg_count = driver.find_element(By.XPATH,'//div[@class="Q1A_pjwq"]/div[2]').text
            try:
                jianjie = driver.find_element(By.XPATH,'//div[@class="lFECd241"]').text
            except:
                jianjie = ''


            # new_zuopin = ''
            try:
                print('进去获取作品页面')
                zuopin = driver.find_element(By.XPATH, '//div[@id="semiTabpost"]//h2/span[2]').text
                if zuopin[-1:] == '万':
                    num = zuopin[:-1]
                    new_zuopin = int(float(num) * 10000)
                elif zuopin[-1:] == '亿':
                    num = zuopin[:-1]
                    new_zuopin = int(float(num) * 100000000)
                else:
                    new_zuopin = zuopin
            except:
                new_zuopin = 0

            ico = ico_img.get_attribute('src')

            if digg_count[-1:] == '万':
                num = digg_count[:-1]
                diggCount = int(float(num) * 10000)
            elif digg_count[-1:] == '亿':
                num = digg_count[:-1]
                diggCount = int(float(num) * 100000000)
            else:
                diggCount = int(digg_count)

            if fensi[-1:] == '万':
                num = fensi[:-1]
                new_fensi = int(float(num) * 10000)
            elif fensi[-1:] == '亿':
                num = fensi[:-1]
                new_fensi = int(float(num) * 100000000)
            else:
                new_fensi = int(fensi)



            data1 = {
              "innerDTOList": [
                {
                  "authorDesc": jianjie,
                  "diggCount": diggCount,
                  "fansCount": new_fensi,
                  "hdiggCount": 0,
                  "hfansCount": 0,
                  "iconUrl": ico,
                  "id": int(data[author_]['id']),
                  "videoCount":new_zuopin
                }
              ]
            }
            # print(data1)
            auth_post = requests.post('https://zt.juzhun.com/admin/authorApi/edit',json=data1)
            print(auth_post.text)
            # print(f'达人名字：{name}'
            #       f'达人简介：{jianjie}'
            #       f'达人粉丝数：{fensi}'
            #       f'达人关注数量：{guanzhu}'
            #       f'达人总赞数：{diggCount}'
            #       f'达人总作品{new_zuopin}'
            #       f'达人头像地址：{ico}')
            # sleep(random.randint(1,5))

        except Exception as ee:
            print(ee)


