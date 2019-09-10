# parser.py
import requests
import re
import sys
import os 
import multiprocessing as mp 
from bs4 import BeautifulSoup
from pprint import pprint 
from datetime import timedelta, date
from time import time 

email = re.compile(r'[a-zA-Z0-9\_\.\-]+@[a-zA-Z0-9\_\.\-]+') # naive email regex 
name = re.compile(r'[가-힣]{2,4}(\s)?기자')

ignore_lines = ['무단 전재-재배포 금지.']


"""
1. 긁어올 날들을 만듬 
"""
def daterange(date1 = date(2016,1,1), date2 = date(2016,2,1)):
    res = []
    for n in range(int ((date2 - date1).days)+1):
        res.append((date1 + timedelta(n)).strftime("%Y%m%d"))
    
    return res

"""
2. 경기를 
"""
def get_links(date, pages = (1, 10)):
    lst = []
    for page in range(*pages):
        # print(page)
        url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&date=%s&page=%s'%(date, page)

        # HTTP GET Request
        req = requests.get(url)
        # HTML 소스 가져오기
        html = req.text
        # BeautifulSoup으로 html소스를 python객체로 변환하기
        # 첫 인자는 html소스코드, 두 번째 인자는 어떤 parser를 이용할지 명시.
        # 이 글에서는 Python 내장 html.parser를 이용했다.
        soup = BeautifulSoup(html, 'html.parser')

        titles = soup.select('dt')
        
        for t in titles:
            lst.append(t.find('a')['href'])
            
    return lst
    
def clean_content(text, writer_email):
    res = []
    for line in text.split('. '):
        if re.match(r'\s*', line) is not None and line != '':
            res.append(line.strip() +'.')
        elif writer_email in line:
            # print(line)
            return res 
    return res 
    
def get_article(link, file = sys.stdout):
    req = requests.get(link)
    html = req.text 
    
    soup = BeautifulSoup(html, 'html.parser')
    
    press = soup.find(attrs = {'class' : 'press_logo'}).find('a').find('img')['title']
    whole_text = soup.get_text()
    writer_email = re.search(email, whole_text)
    if writer_email is None:
        writer_name = 'UNK'
        writer_email = 'UNK'
    else:
        pos = writer_email.span()[0]
        cand = whole_text[pos - 10:pos]
        writer_email = writer_email[0]
        
        writer_name = re.search(name, cand)
        if writer_name is not None:
            writer_name = writer_name[0].replace('기자', '').strip()
        else:
            writer_name = 'UNK'
    
    
    content = soup.find(attrs = {'id' : 'articleBodyContents'})
    try:
        content.script.extract()
        content.span.extract()
    except AttributeError:
        pass 

    image_caption = []
    
    # images = content.find_all('table', attrs = {'name' : 'news_image'})
    while 'table' in [c.name for c in content.children]:
        table = content.table.extract()
        
        if 'name' in table and table['name'] == 'news_image':
            # print(table)
            image_caption.append(table.get_text())
    
    content = clean_content(content.get_text(), writer_email)
    print('press : %s'%press, file = file)
    print('기자명 : %s'%writer_name, file = file)
    print('기자 이메일 : %s'%writer_email, file = file)
    print('기사 내용 시작', file = file)
    sents = []
    for sent in content:
        if writer_email in sent:
            pass
        elif sent in ignore_lines:
            pass 
        else:
            sents.append(sent)
            print(sent, file = file)
    print('기사 내용 끝', file = file)


def crawl_daily_articles(day):
    if not os.path.exists(day):
        os.mkdir(day)
    
    for idx, link in enumerate(get_links(day)):
        f = open(os.path.join(day, str(idx) + '.txt'), 'w+', encoding = 'utf-8')
        get_article(link, f)
    
    
if __name__ == '__main__':
    # lst = get_links('20190719')
    # print(len(lst))
    
    # get_article('https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=001&oid=014&aid=0004264500')
    # get_article('https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=001&oid=469&aid=0000407006')

    todos = daterange()

    """
    print('for loop') # 한달치 2183.39초
    
    os.mkdir('for loop')
    os.chdir('for loop')
    begin = time()
    for day in todos:
        crawl_daily_articles(day)
    end = time()

    print(round(end-begin, 2))


    """
    print('mp') # 한달치 959.04초, cpu 3개 사용 
    
    #os.mkdir('mp')
    os.chdir('mp')
    begin = time()
    
    p = mp.Pool(mp.cpu_count()-1)
    p.map_async(crawl_daily_articles, todos).get()
    end = time()
    
    print(round(end-begin, 2))
    
    