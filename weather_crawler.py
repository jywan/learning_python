# -*- coding: utf-8 -*-
# Time    : 2018/6/1 10:30 PM
__author__ = 'wjy'
"""
爬取和风天气预报数据
website： https://www.heweather.com/
"""
import requests
import time
import pymongo

# 城市搜索
KEY = 'd9330e4953f94365be1f7abd70e6e047'
CID_FIND_URL = 'https://search.heweather.com/find'
WEATHER_FORECAST_URL = 'https://free-api.heweather.com/s6/weather/forecast'


class NoneError(BaseException):
    """
    自定义异常，请求返回空
    """

    def __init__(self, hint=''):
        super().__init__()
        self.hint = hint

    def __str__(self):
        return self.hint


def get_all_city_id():
    cids = []
    with open('china-city-list.txt', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i < 3:
                continue
            cid = line.split('\t')[0]
            cids.append(cid)
    return cids


def get_cid(location='shenz'):
    """
    :param location: default value 'shenzhen'(深圳)
    :return: cid
    """
    params = {
        'key': KEY,
        'location': location
    }
    resp = requests.get(CID_FIND_URL, params=params)
    resp.encoding = 'utf-8'
    data = resp.json()
    # print(resp.encoding)  # 一般是网页指定的编码格式
    # print(resp.apparent_encoding) # 真实的编码，程序自己分析，会比较慢
    # print(data)
    if data['HeWeather6'][0]['status'] == 'ok':
        return data['HeWeather6'][0]['basic'][0]['cid']  # 获取城市的编号cid
    else:
        raise NoneError('none cid, please check the location!')


def weather_forecast(location):
    result = []
    params = {
        'key': KEY,
        'location': location
    }
    resp = requests.get(WEATHER_FORECAST_URL, params=params)
    resp.encoding = 'utf-8'
    data = resp.json()
    forecasts = data['HeWeather6'][0]['daily_forecast']
    # day = {} # 若定义在for循环外面，字典为同一个引用对象，所以最终的值会变成一个
    for cast in forecasts:
        # This dictionary creation could be rewritten as a dictionary literal
        # day = {}  # 关于字典的更新的方法
        # day['date'] = cast['date']  # 预报日期
        # day['tmp_max'] = cast['tmp_max']  # 最高温度
        # day['tmp_min'] = cast['tmp_min']  # 最低温度
        # day['cond_txt_d'] = cast['cond_txt_d']  # 白天天气状况描述
        # day['cond_txt_n'] = cast['cond_txt_n']  # 晚间天气状况描述
        day = {'date': cast['date'], 'tmp_max': cast['tmp_max'], 'tmp_min': cast['tmp_min'],
               'cond_txt_d': cast['cond_txt_d'], 'cond_txt_n': cast['cond_txt_n']}
        # day.update({
        #     'date': cast['date'], 'tmp_max': cast['tmp_max'], 'tmp_min': cast['tmp_min'],
        #     'cond_txt_d': cast['cond_txt_d'], 'cond_txt_n': cast['cond_txt_n']
        # })
        result.append(day)
    return result


# print(get_cid())
# print(weather_forecast('CN101010100'))
# print(len(get_all_city_id()))
if __name__ == '__main__':
    # 建立MongoDB连接
    client = pymongo.MongoClient('localhost', 27017)
    # 创建数据库 weather
    book_weather = client['weather']
    # 创建表 sheet_weather_3
    sheet_weather = book_weather['sheet_weather_3']
    cids = get_all_city_id()
    for i, cid in enumerate(cids):
        weather = weather_forecast(cid)

        sheet_weather.insert_one({cid: weather})
        time.sleep(1)
        if i > 980:  # 受制于每天一千次的访问限制
            break
