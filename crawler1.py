import subprocess
import re
from datetime import datetime
from os import stat_result
from fake_useragent import UserAgent
from openpyxl import load_workbook
import requests
import random
from time import sleep
import threading
import pymysql
import logging, json
from concurrent.futures import ThreadPoolExecutor
import concurrent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置日志级别
file_handler = logging.FileHandler('example1.log')  # 创建一个文件处理器，用于将日志写入文件
file_handler.setLevel(logging.DEBUG)  # 设置文件的日志级别
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # 创建一个formatter并设置日志格式
file_handler.setFormatter(formatter)  # 将formatter设置到handler上
logger.addHandler(file_handler)  # 将处理器添加到记录器中
logger.info('任务计划启动')
print('任务计划启动')
db = pymysql.connect(host="192.168.1.80", port=3306, user="remo80", password="juzhun2023", database="zt")

# db = pymysql.connect(host="172.17.0.142", port=3306, user="jzzt", password="jzzt#2024", database="zt")  # 服务

keywords = ["《", "》", '看后续', '后续', '短剧', '全集', '大结局', '看结局', '全集', '片段', '观看', ':', '完整版',
            '剧情', '点击观看', '结局', '片段', '点我看', '立即观看', '剧情介绍', '免费全集', '免费看',
            '红果短剧', '短句鉴宝', '看全集', '看短剧', '看剧情', '完整版', '-', '花絮', '最新剧情', '【', '】',
            '一口气看完', '最新章节', '点击进入', '点击', '，', '红果免费', '精彩剧集', '查看详情', '免费', '：',
            '更多 ', '！', '·', '-未知', '未知', '热门', '电影']
# ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
uas = UserAgent()
ua = uas.random


def remove_keywords(text, keywords):
    # 将关键字列表转换为正则表达式模式
    pattern = '|'.join(re.escape(kw) for kw in keywords)
    # 使用正则表达式匹配并替换所有关键字
    result_ = re.sub(pattern, '', text)
    return result_


def get_a_bogus_node(data, ua):
    result = subprocess.run(["node", "douyin_ab.js", data, ua], stdout=subprocess.PIPE)
    ab = result.stdout.decode('utf-8').split('\n')[-2]
    return ab


def get_list(sec_user_id, cookies, dy_, mutex):
    logger.info(f'开始爬取达人：{dy_} 下的素材')
    url = 'https://www.douyin.com/aweme/v1/web/aweme/post/'
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "sec_user_id": sec_user_id,
        "max_cursor": "0",
        "locate_query": "false",
        "show_live_replay_strategy": "1",
        "need_time_list": "1",
        "time_list_query": "0",
        "whale_cut_token": "",
        "cut_version": "1",
        "count": "18",
        "publish_video_strategy_type": "2",
        "update_version_code": "170400",
        "pc_client_type": "1",
        "version_code": "290100",
        "version_name": "29.1.0",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_name": "Chrome",
        "browser_version": "128.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "128.0.0.0",
        "os_version": "10",
        "cpu_core_num": "24",
        "device_memory": "8",
        "platform": "PC",
        "downlink": "10",
        "effective_type": "4g",
        "round_trip_time": "50",
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": cookies[random.randint(0, 5)],
        "priority": "u=1, i",
        "referer": "https://www.douyin.com/user/{}".format(sec_user_id),
        "sec-ch-ua": "Not/A)Brand;v=8, Chromium;v=126, Google",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows^",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua,
    }
    param_list = []
    for param_key, params_value in params.items():
        param_list.append(f'{param_key}={params_value}')
    has_more = 1
    err_count = 0
    while True:
        if has_more == 1 or has_more == 0:
            try:
                data_str = '&'.join(param_list)
                ab = get_a_bogus_node(data_str, ua)
                params['a_bogus'] = ab
                response = requests.get(url, params=params, headers=headers)
                result = response.json()
                has_more = result['has_more']
                params['max_cursor'] = result['max_cursor']
                news_list = result.get('aweme_list')
                if len(news_list) != 0:
                    for data_lists in news_list:
                        date_time = data_lists["create_time"]
                        dt_object = datetime.fromtimestamp(date_time)
                        # 设置一个阈值，代表三天的秒数
                        threshold = 3 * 24 * 60 * 60
                        # 当前时间
                        now = datetime.now().timestamp()
                        if now - date_time > threshold:
                            if data_lists['is_top'] == 1:
                                # logger.info('置顶检测')
                                pass
                            else:
                                return '超过三天'
                        else:
                            try:
                                videos = data_lists['video']['play_addr_h264']['url_list']
                                ratio_width = data_lists['video']['width']
                                ratio_height = data_lists['video']['height']
                                ratio = str(ratio_width) + '*' + str(ratio_height)
                                playlet_size = data_lists['video']['play_addr_h264']['data_size']
                            except:
                                try:
                                    videos = data_lists['video']['play_addr']['url_list']
                                except:
                                    videos = ''
                                try:
                                    ratio_width = data_lists['video']['width']
                                    ratio_height = data_lists['video']['height']
                                    ratio = str(ratio_width) + '*' + str(ratio_height)
                                except:
                                    ratio = ''
                                try:
                                    playlet_size = data_lists['video']['play_addr']['data_size']
                                except:
                                    playlet_size = ''
                            try:
                                comment_count = data_lists["statistics"]["comment_count"]  # 评论
                            except:
                                comment_count = 0
                            try:
                                digg_count = data_lists["statistics"]["digg_count"]  # 点赞
                            except:
                                digg_count = 0
                            try:
                                collect_count = data_lists["statistics"]["collect_count"]  # 收藏
                            except:
                                collect_count = 0
                            try:
                                suggest_words = data_lists["suggest_words"]["suggest_words"]  # 剧名
                                suggest_word = suggest_words[len(suggest_words) - 1]["words"][0]["word"]
                            except:
                                try:
                                    suggest_word = data_lists["anchor_info"]["title"] #库名
                                except:
                                    suggest_word = '未分类'

                            mutex.acquire()
                            try:
                                clean_text = remove_keywords(suggest_word, keywords) #库名字符匹配
                                if clean_text == '': #判断库名是否为空
                                    clean_text = '未分类'
                                dy_ju_id = data_lists['aweme_id'] #获取抖音视频ID
                                playlet_title = data_lists["desc"] #获取内容
                                video_url = videos[len(videos) - 1] #视频下载的url
                                share_url = data_lists["share_url"] #抖音内嵌的URL
                                durations = data_lists['duration'] #视频时常
                                duration = float(int(durations) / 1000)
                                minute = float(duration) // 60
                                second = float(duration) % 60
                                dura = f'{str(int(minute))}:{str(int(second))}'
                                text_tags = data_lists['text_extra'] #视频标签
                                tag = ''
                                if text_tags != 'null':
                                    for text_tag in text_tags:
                                        try:
                                            tag += '#' + text_tag['hashtag_name']
                                        except:
                                            pass
                                # 获取当前日期和时间
                                now = datetime.now()
                                # 打印当前日期和时间到分钟
                                now_date = now.strftime('%Y-%m-%d %H:%M:%S')
                                if clean_text != '未分类':
                                    select_new_third_data = f"select id from zt_third_drama WHERE playlet_name='{clean_text}'"
                                    cursor.execute(select_new_third_data)
                                    chaxun_shuju = cursor.fetchall()
                                    if len(chaxun_shuju) == 0:
                                        new_third_name = f"INSERT INTO zt_third_drama (playlet_name,plat_name,comment_count,digg_count,collect_count) VALUES ('{clean_text}','未知',0,0,0)"
                                        cursor.execute(new_third_name)
                                        db.commit()
                                        logger.info(f'新增库名：{clean_text}')
                                        cursor.execute(select_new_third_data)
                                        new_cleam_text = cursor.fetchall()
                                        ju_id = new_cleam_text[0][0]
                                    else:
                                        cursor.execute(select_new_third_data)
                                        new_cleam_text = cursor.fetchall()
                                        ju_id = new_cleam_text[0][0]
                                        logger.info(f'库名存在ID为：{ju_id}')
                                else:
                                    ju_id = 0
                                    clean_text = ' '
                                    logger.info(f'判断分类，应该为{ju_id},playlet_name应该为空{clean_text}')
                                sql1 = 'SELECT * FROM zt_author_data WHERE video_id={}'.format(dy_ju_id)
                                cursor.execute(sql1)
                                video_id = cursor.fetchall()
                                if len(video_id) == 0:
                                    playlet_title = playlet_title.replace("'", '')
                                    insert_sql = f"INSERT INTO zt_author_data (drama_id, author_uid, playlet_title, playlet_name, playlet_url, issue_time,create_time,update_time, comment_count, digg_count, collect_count, three_comment_count, three_digg_count,three_collect_count, video_id,playlet_tag,playlet_duration,playlet_resolution_ratio,playlet_size) VALUES ({ju_id},'{dy_}','{playlet_title}','{clean_text}','{video_url}','{dt_object}','{now_date}','{now_date}',{comment_count},{digg_count},{collect_count}, 0, 0, 0, {dy_ju_id},'{tag}','{dura}','{ratio}','{playlet_size}')"
                                    cursor.execute(insert_sql)
                                    db.commit()
                                    logger.info(f'新增数据：剧ID{ju_id} 达人名字{dy_}')
                                else:
                                    up_id = video_id[0][0]
                                    new_comment_count = comment_count - video_id[0][9]
                                    new_digg_count = digg_count - video_id[0][10]
                                    new_collect_count = collect_count - video_id[0][11]
                                    update_sql = f"UPDATE zt_author_data SET drama_id={ju_id}, update_time = '{now_date}', comment_count = {comment_count},digg_count = {digg_count}, collect_count = {collect_count}, three_comment_count = {new_comment_count}, three_digg_count = {new_digg_count},three_collect_count = {new_collect_count} WHERE id = {up_id}"
                                    cursor.execute(update_sql)
                                    db.commit()
                                    logger.info(f'更新数据，库名id:{ju_id} 达人抖音号：{dy_} 抖音视频ID:{dy_ju_id}')
                            except Exception as e:
                                mutex.release()
                                logger.error(f'{e}入库时报错')
                                return str(e)
                            mutex.release()
                            if has_more == 0:
                                return '最后一页了'
                else:
                    sleep(random.randint(3, 5))
            except Exception as e:
                if str(e) == "'has_more'":
                    logger.error('可能是私密账号')
                    print('可能是私密账号')
                    return '可能是私密账号'
                if str(e) == 'Expecting value: line 1 column 1 (char 0)':
                    headers["cookie"] = cookies[random.randint(0, 5)]
                    err_count += 1
                    if err_count >= 3:
                        #     logger.error(f'错误警报，cookies池随机8次未成功')
                        return 'cookies池随机3次未成功'
                else:
                    return
                if has_more == 0:
                    return '最后一页报错了'

                logger.error(f'{e}----------{sec_user_id}')
        if has_more == 0:
            return '最后一页退出'


if __name__ == '__main__':
    cookies = []
    dy_ids = []
    # 创建线程列表
    threads = []
    sec_user_ids = []
    with open('dy_cookie.txt', 'r') as f:
        for line in f:
            cookies.append(line.split('\n')[0])
    f.close()
    cursor = db.cursor()
    mutex = threading.Lock()


    author_data_url = "SELECT author_uid,author_url FROM `zt_author` WHERE author_uid!='' and status_flag=1"
    cursor.execute(author_data_url)
    author_url = cursor.fetchall()
    nnum = len(author_url) / 2
    # nnum2 = int(nnum) / 2
    for author_ in range(int(nnum), len(author_url)):

        print(author_url[author_])
    # for author_ in range(int(nnum), int(nnum2) + int(nnum)):
    # for author_ in range(0, int(nnum)):
    #     ceshi = author_url[author_][1].split('/')
    #     dy_id = author_url[author_][0]
    #     sec_user_id = ceshi[len(ceshi) - 1]
    #     dy_ids.append(dy_id)
    #     sec_user_ids.append(sec_user_id)
    #
    # with ThreadPoolExecutor(max_workers=12) as executor:
    #     # 提交请求任务到线程池
    #     future_to_url = {executor.submit(get_list, user_ids, cookies, dy_id, mutex): [user_ids, dy_id] for
    #                      user_ids, dy_id in zip(sec_user_ids, dy_ids)}
    #     concurrent.futures.wait(future_to_url)
    #     executor.shutdown()
    #
    #
    #
    # logger.info('执行完毕')
    # print('执行完毕')
    # cursor.close()
    # db.close()









