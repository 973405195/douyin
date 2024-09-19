import sys
import subprocess
from fake_useragent import UserAgent
import pymysql
from concurrent.futures import ThreadPoolExecutor
import concurrent
import random,requests
from time import sleep
from lxml import etree
import re,json
from datetime import datetime

uas = UserAgent()
cookies = []
def get_a_bogus_node(data, ua):
    result = subprocess.run(["node", "douyin_ab.js", data, ua], stdout=subprocess.PIPE)
    ab = result.stdout.decode('utf-8').split('\n')[-2]
    return ab

def analysis_args(video_url):

    ua = uas.random
    url = 'https://www.douyin.com/user/self'
    data = {
        "from_tab_name":'main',
        'modal_id':video_url
    }

    ck = cookies[random.randint(10, 20)]
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": ck,
        "priority": "u=1, i",
        "path": f"/user/self?from_tab_name=main&modal_id={video_url}",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows^",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua,
    }


    while_num = 0
    while while_num<5:
        try:
            response = requests.get(url, params=data, headers=headers).text
            result = re.findall(r'\\"stats\\":(.*?),\\"shareInf',response)
            diggcount = re.findall(r'diggCount\\":(.*?),',result[0])[0]  #点赞数量
            commentCount = re.findall(r'commentCount\\":(.*?),',result[0])[0]  #评论数量
            collect_count = re.findall(r'collectCount\\":(.*?),',result[0])[0] #收藏数量
            # print(f'{video_url}该作品点赞数量：{diggcount} 评论数量：{commentCount} 收藏数量：{collect_count}')
            return diggcount,commentCount,collect_count,video_url
            # sleep(random.randint(3,5))
            # return digg_count,comment_count,collect_count
        except Exception as e:
            sleep(random.randint(1,3))
            while_num+=1
            headers["user-agent"] = uas.random



def main_spider(argv):
    # 服务器数据库
    # db = pymysql.connect(host="172.17.0.142", port=3306, user="jzzt", password="jzzt#2024", database="zt")  # 服务

    #连接本地数据库
    db = pymysql.connect(host="192.168.1.80", port=3306, user="remo80", password="juzhun2023", database="zt")
    cursor = db.cursor()

    #查询改库下所有视频
    # drama_sql = f"SELECT * FROM zt_author_data WHERE drama_id={argv[0]}"
    #查询该库下当天的视频
    drama_sql = f"SELECT * FROM `zt_author_data` WHERE DATE(issue_time) = CURDATE() and drama_id={argv[0]}"
    cursor.execute(drama_sql)
    drama_video_list = cursor.fetchall()

    # 查询cookies
    cks = 'SELECT cookie FROM zt_dy_cookies WHERE status=1'
    cursor.execute(cks)
    cookie_s = cursor.fetchall()
    for cook in cookie_s:
        cookies.append(cook[0])


    videos = []
    for video in drama_video_list:
        videos.append(video[15])


    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交请求任务到线程池
        future_to_url = {executor.submit(analysis_args, video_url,) : video_url for video_url in videos}
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_url):
            thread_ = future_to_url[future]

            try:
                status_code = future.result()
                digg_count = status_code[0]
                comment_count = status_code[1]
                collect_count = status_code[2]
                video_url = status_code[3]
                # sql1 = 'SELECT * FROM zt_author_data WHERE video_id={}'.format(video_url)
                # cursor.execute(sql1)
                # video_id = cursor.fetchall()
                # new_comment_count = int(comment_count) - video_id[0][9]
                # new_digg_count = int(digg_count) - video_id[0][10]
                # new_collect_count = int(collect_count) - video_id[0][11]
                # print(f'{video_url}该作品点赞数量：{digg_count} 评论数量：{comment_count} 收藏数量：{collect_count}----------------')
                # 获取当前日期和时间
                now = datetime.now()
                # 打印当前日期和时间到分钟
                now_date = now.strftime('%Y-%m-%d %H:%M:%S')
                update_sql = f"UPDATE zt_author_data SET update_time = '{now_date}', comment_count = {int(comment_count)}, digg_count = {int(digg_count)}, collect_count = {int(collect_count)} WHERE video_id = {video_url}"
                cursor.execute(update_sql)
                db.commit()
                print(f'{video_url}该作品点赞数量：{digg_count} 评论数量：{comment_count} 收藏数量：{collect_count}')
                # sleep(random.randint(1,2))
            except Exception as exc:
                print(exc)
        concurrent.futures.wait(future_to_url)
    return '程序执行完毕'

# main_spider([4994])
# main_spider(sys.argv[1:])
# analysis_args()



