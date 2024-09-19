from selenium import webdriver
from tkinter import messagebox, Label
import threading,random
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service




import tkinter,requests

root = tkinter.Tk()
root.title('巨准科技：抖音cookies获取')
# root.geometry('400x300')

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 300) / 2
y = (screen_height - 200) / 2
root.geometry(f"{500}x{300}+{int(x)}+{int(y)}")

global text_box

text_box = tkinter.Text(root, height=10, width=40)
text_box.grid(row=1,column=2,pady=30)


text_ = tkinter.Label(root,text='输入抖音号所属人:')
text_.grid(row=0,column=1,pady=10)

entry = tkinter.Entry(root)  # 创建输入框
entry.grid(row=0,column=2,pady=10)

def douyin():
    url = 'https://www.douyin.com/?recommend=1'
    global driver
    global title_name
    title_name = '抖音'
    text_box.delete('1.0', tkinter.END)
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(r'C:\Users\李亚航\AppData\Local\Programs\Python\Python37-32\chromedriver.exe')
    driver = webdriver.Chrome(options=options,service=service)
    driver.get(url)
    driver.maximize_window()


def kuaishou():
    url = 'https://www.kuaishou.com/new-reco'
    global driver
    global title_name
    title_name = '快手'
    text_box.delete('1.0', tkinter.END)
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(options=options, service=service)
    driver.get(url)
    driver.maximize_window()

def zhuaqu():
    print(title_name)

    try:
        global driver
        text_box.delete('1.0', tkinter.END)
        # 获取所有cookies
        cookies_list = driver.get_cookies()
        print(cookies_list)
        # 将cookies转换为字符串
        cookie_str = ''
        for cookie in cookies_list:
            cookie_str += f"{cookie['name']}={cookie['value']}; "
        # 打印字符串格式的cookies
        # messagebox.showinfo("提示", cookie_str)

        name = entry.get()
        url = 'https://zt.juzhun.com/admin/cookies/saveCookies'
        if title_name == '抖音':
            data = {
                "name": name,
                "cookie": cookie_str,
                "cookiesType":1
            }
        else:
            data = {
                "name": name,
                "cookie": cookie_str,
                "cookiesType":2
            }

        requests.post(url,json=data)
        text_box.insert(tkinter.END, cookie_str)
        messagebox.showinfo("提示", "获取成功已自动保存数据库")
        text_box.delete('1.0', tkinter.END)
        entry.delete(0, tkinter.END)
        driver.quit()
    except Exception as e:
        print(e)
        messagebox.showinfo("提示", "程序错误")

def thread_start_check(start_check):
    t1 = threading.Thread(target=start_check, args=())
    t1.start()




button1 = tkinter.Button(root,text="抖音启动",font=('微软雅黑',20),command=lambda :thread_start_check(douyin))
button1.grid(row=2,column=1)
button1 = tkinter.Button(root,text="快手启动",font=('微软雅黑',20),command=lambda :thread_start_check(kuaishou))
button1.grid(row=2,column=2)
# button1.pack()

button1 = tkinter.Button(root,text="获取",font=('微软雅黑',20),command=lambda :thread_start_check(zhuaqu))
button1.grid(row=2,column=3)
# button1.pack()
# 进入消息循环
root.mainloop()