import datetime
import time
import ddddocr    # 导入 ddddocr
import requests
from loguru import logger

from getS_numberAndCookie import getValue
from tools.ConfigManager import ConfigManager
from tools.log import log_print
print = log_print

config_manager = ConfigManager()

S_number, cookie = getValue()

if S_number is None:
    logger.error("获取cookie失败")
    exit(0)

# 使用需要登录系统，然后替换S_number和cookie
# S_number = config_manager.get_param("info", "S_number", "用后面url中的S_number替换 http://gmis.buct.edu.cn/(S({S_number}))/student/yggl/xshdbm_sqlist")

# cookie = config_manager.get_param("info", "cookie", "随便找一个请求，类似 __SINDEXCOOKIE__=be877f28c010fdc2e910c2171ff420ea")
key_words = config_manager.get_param("paper", "name_keywords", '榜样引航校友论坛系列第27与28场,榜样引航校友论坛系列第29与30场')


ids = []
img_path = "./img_ss.png"  # 验证码图片
index = 1  # 选择列表的第几个学术报告
gap_time = 1  # 间隔时间，单位是秒，可以自己调整

# 设置请求头
headers = {
    'Cookie': cookie,
    'Pragma': "no-cache",
    'X-Requested-With': "x_requested_with",
    'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8"
}

def get_list():  # 获取学术报告id列表
    # 构建完整的 URL
    url = f"http://gmis.buct.edu.cn/(S({S_number}))/student/yggl/xshdbm_sqlist"

    # 发送请求
    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        logger.exception("请检查检查config.ini中的S_number")
        exit(0)
    id_rows = []  # 返回的id列表

    # 检查请求是否成功
    if response.status_code == 200:
        response = response.json()
        # 处理响应内容
        print(response)
        id_rows = []
        for i in range(len(response['rows'])):
            id_rows.append({
                'id': response['rows'][i]['id'],
                'name': response['rows'][i]['mc'],
                'start': response['rows'][i]['bmkssj'],
                'end': response['rows'][i]['bmjzsj'],
            })
    else:
        print(f"Error: {response.status_code}")
    print("获取的报告id列表: ", id_rows)
    return id_rows

def send_bark(msg):
    base_url = config_manager.get_param("system", "bark_url", "https://api.day.app/8WfiKM8ZJzpvYYRkHiXpyS")
    url = f"{base_url}/{msg}"
    requests.get(url)

def valid():
    url = f"https://gmis.buct.edu.cn/(S({S_number}))/student/default/getxscardinfo"
    response = requests.get(url, headers=headers)
    try:
        response.json()
    except:
        return False, None
    return True, response.json()[0]

def get_VerificationCode():  # 获取验证码
    url = f"http://gmis.buct.edu.cn/(S({S_number}))/student/yggl/VerificationCode"

    response = requests.get(url, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        # 假设响应内容是图片的二进制数据
        with open(img_path, 'wb') as f:
            f.write(response.content)
        print("验证码已保存为 img_ss.png")
    else:
        print(f"Error: {response.status_code}")


def send_post_request(id, VeriCode):  # 抢报告
    url = f"http://gmis.buct.edu.cn/(S({S_number}))/student/yggl/xshdbm_bm"

    # 构建POST请求的数据
    data = {
        'id': id,
        'VeriCode': VeriCode
    }

    # 发送POST请求
    response = requests.post(url, data=data, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        print("请求成功，响应内容：", response.text)
    else:
        print(f"Error: {response.status_code}")


def ocr_number(img_path):  # 调取ocr识别图片验证码
    ocr = ddddocr.DdddOcr()              # 实例化
    with open(img_path, 'rb') as f:     # 打开图片
        img_bytes = f.read()             # 读取图片
    res = ocr.classification(img_bytes)  # 识别
    print(res)

    lines = res.splitlines()  # 将字符串拆分成多行
    last_line = lines[-1]  # 获取最后一行
    print(last_line)  # 打印最后一行

    return last_line

def is_time_in_range(start_time_str, end_time_str, time_format="%Y-%m-%d %H:%M:%S"):
    # 将字符串转换为 datetime 对象
    start_time = datetime.datetime.strptime(start_time_str, time_format)
    logger.debug(f"start_time={start_time}")
    # 将开始时间提前
    start_time -= datetime.timedelta(minutes=4)

    end_time = datetime.datetime.strptime(end_time_str, time_format)
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 检查当前时间是否在范围内
    return start_time <= current_time <= end_time

def is_time_in_range_3_min(start_time_str, time_format="%Y-%m-%d %H:%M:%S"):
    # 将字符串转换为 datetime 对象
    start_time = datetime.datetime.strptime(start_time_str, time_format)

    # 将开始时间提前
    # start_time -= datetime.timedelta(minutes=4)
    # end_time
    # end_time = datetime.datetime.strptime(end_time_str, time_format)
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 检查当前时间是否在范围内
    logger.debug(f"抢的时间范围={start_time - datetime.timedelta(seconds=15)} {start_time + datetime.timedelta(seconds=15)}")
    return start_time - datetime.timedelta(seconds=15) <= current_time <= start_time + datetime.timedelta(seconds=15)

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    logger.add("./log/学术报告/log-{time:YYYY-MM-DD}.log", rotation="10 MB", retention=10)
    logger.add("./log/学术报告/error/log-{time:YYYY-MM-DD}.log", level="ERROR")
    # valid_flag, user_info = valid()
    # logger.info(f"{valid_flag} {user_info['xm']}")
    paper_list = get_list()  # 获取可选报告id列表
    times = 0
    while True:

        if times % 600 == 0:
            valid_flag, user_info = valid()
            logger.info(f"{valid_flag} {user_info['xm']}")
            if valid_flag == False:
                logger.error("用户cookie失效")
                send_bark("用户cookie失效")
                S_number, cookie = getValue()
                valid_flag, user_info = valid()
                if valid_flag == True:
                    send_bark("用户cookie已经重新获取")
                else:
                    send_bark("用户cookie重新获取失败")

                    exit(0)
            else:
                send_bark(f"抢学术报告系统稳定运行 {user_info['xm']}")
        times += 1

        for paper in paper_list:
            contains_keyword = any(keyword in paper['name'] for keyword in key_words)
            logger.debug(f"是否包含关键字 {contains_keyword} {paper['name']}")
            if contains_keyword:
                print(contains_keyword, paper)
                start_time = paper['start']
                end_time = paper['end']
                logger.info(f"准备报名 {paper['id']} {paper['name']} {start_time} {end_time}")
                if is_time_in_range_3_min(start_time):
                    get_VerificationCode()
                    VeriCode = ocr_number(img_path)
                    send_post_request(paper['id'], VeriCode)
                    send_bark(f"报名 {paper['id']} {paper['name']} {start_time} {end_time}")
                else:
                    logger.debug("报名失败 不在指定时间内，等待中...")
        time.sleep(gap_time)  # 这是睡眠时间，单位是秒，可以自己调整

