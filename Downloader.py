import requests
import json
import queue
import threading
import math
import DataPersistance
from lxml import etree

import Config

persistance = DataPersistance.DataPersistance()

Q = queue.Queue()
Q_url = queue.Queue()

categoryCd = 'CA01'
per = 20
global page
page = 1


def get_page():
    global page
    total_page = int(math.floor(total_row / per))
    for i in range(total_page):
        page += 1
        data = create_data()
        requests_post(data)



def create_data():
    data = {
        'searchKey': '',
        'categoryCd': categoryCd,
        'selectCategory': '',
        'page': page,
        'spCategoryCode': '',
        'spSeries': ''
    }

    return data

# def request_detail():
#     response = requests.get(url)
#     print(response.text)


def test(url,pn):
    headers = {
        'Host': 'www.ket.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.ket.com/en/product/feature-search.ket?categoryCd=CA01',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cookie': 'JSESSIONID=3502457241A1F141CE25171598C756F7; language=en; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en'
    }
    response = requests.get(url, headers=headers)
    body = etree.HTML(response.text)
    d2_xpath = body.xpath('//*[@id="container"]/div[3]/div[1]/dl/dd[2]/div[2]/span[1]/a/@href')
    d3_xpath = body.xpath('//*[@id="container"]/div[3]/div[1]/dl/dd[2]/div[2]/span[2]/a/@href')
    # if len(d2_xpath) == 0:
    #     d2_xpath[0] = None
    # if len(d3_xpath) == 0:
    #     d3_xpath[0] = None
    persistance.add_data(pn,d2_xpath,d3_xpath)


def requests_post(data):
    response = requests.post(Config.ROOT_URL, data=data, headers=Config.headers_root)
    parser_json(response.text)

def request_detail():
    while not Q.empty():
        url = Config.DETAIL_URL + Q.get()
        # test(url)
        t = threading.Thread(target=test(url,Q.get()))
        t.start()
    get_page()


def parser_html(text):
    pass

global total_row
def parser_json(response):
    loads = json.loads(response)
    global total_row
    total_row = loads['result']['searchInfo']['totalRow']
    # print(create_data())
    lists = loads['result']['list']
    for i in range(len(lists)):
        partnumber = lists[i]['PARTNUMBER']
        Q.put(partnumber)
    request_detail()

if __name__ == '__main__':
    response = requests.post(Config.ROOT_URL, data=create_data(), headers=Config.headers_root)
    parser_json(response.text)


