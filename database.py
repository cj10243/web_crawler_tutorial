# -*- coding: utf-8 -*-
# /usr/bin/python3
import pymysql
import os

class Database:
    def __enter__(self):
        self.conn = pymysql.connect(
                            host='localhost',
                            port=3306,
                            user='user',
                            passwd='passwd',
                            db='db',
                            use_unicode=True,
                            charset="utf8")

        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, ex_type, ex_value, ex_tb):
        self.conn.commit()
        self.conn.close()

def query_fetchone(sql,data=None):
    with Database() as db:
        if data:
            db.execute(sql,data)
        else:
            db.execute(sql)
        return db.fetchone()
def query_fetchall(sql,data=None):
    with Database() as db:
        if data:
            db.execute(sql,data)
        else:
            db.execute(sql)
        return db.fetchall()
def insert_weather(data):
    with Database() as db:
        sql = """INSERT INTO weather (time,id,tpr,wet,uv) VALUES (%s,%s,%s,%s,%s)"""
        db.execute(sql,data)

#table database.weather
'''
create table weather ( time timestamp default current_timestamp on update current_timestamp,
                id smallint ,
                tpr float(3,1),
                wet float(3,1),
                uv tinyint(2),
                 foreign key (id) references chatbot.station(pk));
'''



'''
MySQL database.station
----------------------
CREATE TABLE station(
    pk SMALLINT(5) NOT NULL AUTO_INCREMENT,
    name VARCHAR(5) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    station_id VARCHAR(6),
    lng DOUBLE(10,6),
    lat DOUBLE(10,6),
    PRIMARY KEY(pk));
'''