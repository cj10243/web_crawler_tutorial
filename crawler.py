# -*- coding: utf-8 -*-
# /usr/bin/python3
import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime,timedelta
import re
import pymysql
import database
import re


def get_soup(url):
    res = requests.get(url)  # 從網址存網站頁面
    res.encoding = 'utf-8'  # 修正requests和bs4自行猜測的編碼為utf-8
    soup = BeautifulSoup(res.text, "lxml")  # 存成文字內容
    return soup
def weather_crawler(id,weather_id):
    url = "http://www.cwb.gov.tw/V7/observe/24real/Data/{}.htm".format(weather_id)
    tw_soup = get_soup(url)# tpr+wet
    url = "http://www.cwb.gov.tw/V7/observe/UVI/UVI.htm"
    uv_soup = get_soup(url)# uv
    db_time = get_newest_time_from_db(id)
    count = 0
    data_set = []
    for i in tw_soup.table.tr.next_siblings:
        if i == '\n':
            pass
        else:
            print("weather_crawler: 主鍵id={}".format(id))
            time = str(i).split("</th>")[0].split(">")[2]
            year = datetime.now().year
            print("year{}".format(year))
            print("time{}".format(type(time)))
            time = datetime.strptime('{} {}'.format(year,time), '%Y %m/%d %H:%M')
            print("weather_crawler: 時間： {}".format(time))  # ex: 2017-05-29 13:30:00
            tpr = str(i).split("</td>")[0].split(">")[4]  # 攝氏溫度 ex:29.5
            #print("攝氏溫度： {}".format(tpr))
            wet = str(i).split("</td>")[1].split(">")[1]
            #print("相對溼度： {}".format(wet))  # 相對溼度 ex:85.1
            uv_soup.find("span", id="Data_{}".format(weather_id))
            pat = '\d+'
            string = uv_soup.find("span", id="Data_46691").get_text()
            match = re.findall(pat, string)
            if match:
                uv = int(match)
            else:
                uv = None
            '''
            try:
                uv = int(uv_soup.find("span", id="Data_{}".format(weather_id)).get_text().split(" ")[3])
            except AttributeError as error:
                # 取不出字時　ex: uv = -
                print("weather_crawler:: 紫外線：{}".format(error))
                uv = None
            except ValueError as error:
                print("{}".format(error))
                uv = uv_soup.find("span", id="Data_{}".format(weather_id)).get_text()
            else:
                # 兩種情況：數字或文字　ex:1. uv=3 ;2. uv=機器維修
                uv = int(uv)
            '''
            print("weather_crawler:紫外線值： {}".format(uv))
            data = []
            print("測試:　時間{}溫度{}濕度{}紫外線直{}".format(time,tpr,wet,uv))

            data.extend([time,id,tpr,wet,uv])
            print("單筆：{}".format(data))
            data_set.append(data)
    print("資料集{}".format(data_set))
    return data_set#回傳50筆資料

def get_uv_image():
    pass
def get_newest_time_from_db(id):
    with database.Database() as db:
        sql = """SELECT DISTINCT COUNT(*) FROM  weather where id = {} order by time desc;""".format(id)
        db.execute(sql)
        space = db.fetchone()[0]  # 檢驗是否為空的資料庫
        sql = """SELECT DISTINCT * FROM  weather where id = {} order by time desc;""".format(id)
        db.execute(sql)
        if space:
            try:
                db_time = db.fetchone()[0]
            except TypeError as error:
                print(" 此筆時間格式有誤：{}".format(error))
                db_time = None
            else:
                print("資料庫最新一筆資料為：{}".format(db_time))
            finally:
                return db_time
        else:
            return 0
def check_newest_weather(id,weather_id):
    data_set = weather_crawler(id, weather_id)
    db_time = get_newest_time_from_db(id)
    print("check_newest_weather: 資料庫最新一筆資料時間：{}".format(db_time))
    if db_time == 0:
        print("空資料庫")
        for i,j in enumerate(data_set):
            print("第{}筆資料{}插入".format(i,j))
            try:
                database.insert_weather(tuple(j))
            except Exception as err:
                print("{}".format(err))
    elif db_time == None:
        print("日期有問題！！！快去檢查")
    else:
        check = 0
        for i, j in enumerate(data_set):
            print("資料庫最新時間；{}".format(db_time))
            print("網路上最新時間：{}".format(j[0]))
            if j[0] > db_time:
                print("資料待更新")
                if j[0] - db_time == timedelta(minutes=15):
                    print("資料符合順序")
                    new_data = data_set[:i]
                    for k,l in enumerate(new_data):
                        print("第{}筆資料插入".format(k))
                        check = 1
                        database.insert_weather(tuple(l))
            else:
                print("已更新")
                check=1
                break
        if(not check):
            print("資料落後過多，增加整頁資料")
            for i, j in enumerate(data_set):
                if j[0] != db_time:
                    print("第{}筆資料插入".format(i+1))
                    database.insert_weather(tuple(j))


def station_crawler():
    url = "http://www.cwb.gov.tw/V7/observe/real/ObsN.htm"#北部
    soup = get_soup(url)
    print(soup.find("table",id=63).findAll("a"))
    for i in soup.find("table",id=63).findAll("a"):
        name = i.get_text()
        print(name) #ex: 鞍部
        station_id = i['href'].split(".")[0]
        #print(i['href'].split(".")[0]) #ex:46691
        url = "http://www.cwb.gov.tw/V7/google/{}_map.htm".format(station_id)
        soup = get_soup(url)
        lng_pat = 'lon=\d+.\d+'
        lng = find(lng_pat, str(soup))
        lng = float(lng[0].split("=")[1])
        lat_pat = 'lat=\d+.\d+'
        lat = find(lat_pat, str(soup))
        lat = float(lat[0].split("=")[1])
        print(lng)
        print(lat)

        print(station_id) #ex:46691
        #url = "http://www.cwb.gov.tw/V7/observe/real/{}.htm#ui-tabs-3".format(station_id)

        with database.Database() as db:
            print("name: {} station:{} lng: {} lat: {}".format(name,station_id,lng,lat))
            sql = """SELECT  * FROM  station"""
            db.execute(sql)
            sql = """INSERT INTO station (name,station_id, lng,lat) VALUES (%s,%s,%s,%s)"""
            #sql = """UPDATE  station SET lng=%s , lat=%s where station_id=%s;"""
            #注意SET lng=%s and lat=%s寫法錯誤
            db.execute(sql, (name,station_id,lng,lat))
            #121.575728, 25.00235
def iter_station():
    with database.Database() as db:
        sql = """SELECT pk,station_id FROM  station """
        out = db.execute(sql)
        print(out)
        for i in db.fetchall():
            pk = i[0]
            station_id = i[1]
            print("主鍵{}".format(pk))
            print("測站id{}".format(station_id))
            check_newest_weather(pk,station_id)



def test():
    station_id = "46691"
    url = "http://www.cwb.gov.tw/V7/google/{}_map.htm".format(station_id)
    soup = get_soup(url)
    print(str(soup).find("lon="))
    lng_id = str(soup).find("lon=")
    lat_id = str(soup).find("lat=")
    # print(lat_id)
    # print(str(soup)[lng_id+4:lng_id+15])
    lng = float(str(soup)[lng_id + 4:lng_id + 13])
    lat = float(str(soup)[lat_id + 4:lat_id + 12])
    print(lng)
    print(lat)


def find(pattern,string):
    match = re.findall(pattern, string)
    if match:
        print("find re {}".format(match))
        return match
    else:
        print("none")
        return None


#weather_crawler(102,"C0AC4")
#test()
#test_statement()
iter_station()
#station_crawler()