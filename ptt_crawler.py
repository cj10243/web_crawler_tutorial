# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

class SomeError(Exception):
    pass

def get_article(board,limit,page=-1,count=0,first=True,lst=[]):
    if limit == count or page == 0:
        print("共{}筆文章".format(len(lst)))
        print("已爬了{}頁".format(count))
        print("拜拜")
        return lst,count
    if first:
        print("第1次擷取")
        res = requests.get('https://www.ptt.cc/bbs/{}/index.html'.format(board))
        
    else:
        print("第{}次擷取".format(count+1))
        res = requests.get('https://www.ptt.cc/bbs/{}/index{}.html'.format(board,page))
    if res.status_code != 200:
        print("頁面不存在")
        return 
    elif first:    
        print("第1頁")
        soup = BeautifulSoup(res.text,"lxml")
        print(soup.select('.r-ent'))
        lastpg = int(soup.findAll("a",{"class":"btn wide"})[1]['href'].split('/')[3].split('.')[0][5:])
        nowpg = lastpg + 1
        first = False
        lst = add_info(soup,lst)
        get_article(board,limit,nowpg-1,count+1,first)
    else:
        print("第{}頁".format(count+1))
        soup = BeautifulSoup(res.text,"lxml")
        #soup.find("div",{"class": {"r-ent"}})
        lst = add_info(soup,lst)
        get_article(board,limit,page-1,count+1,first,lst)

def add_info(soup,lst):
    for i in soup.select('.r-ent'):
        local_lst = []
        try:
            local_lst.append(i.find("a").get_text())
        except:
            local_lst.append(None)
        local_lst.append(i.find("div",{"class":"date"}).get_text())
        local_lst.append(i.find("div",{"class":"author"}).get_text())
        try:
            local_lst.append('https://www.ptt.cc'+i.find("a")['href'])
        except:
            pass
        print(local_lst)
        lst.append(local_lst)
    return lst
            
        
def get_total(soup):
    lastpg = int(soup.findAll("a",{"class":"btn wide"})[1]['href'].split('/')[3].split('.')[0][5:])
    nowpg = lastpg + 1
    return nowpg
        

#lst,count = get_article("Python",1)
print(type(get_article("Tennis",1)))
