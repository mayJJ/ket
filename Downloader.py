import requests
import json
import queue
import threading
import math
import DataPersistance
from lxml import etree
from multiprocessing.dummy import Pool as ThreadPool
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
    total_page = int(math.ceil(total_row / per))
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


def test(url):
    headers = {
        'Host': 'www.ket.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.ket.com/en/product/feature-search.ket?categoryCd=CA01',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cookie': 'JSESSIONID=3502457241A1F141CE25171598C756F7; language=en; '
                  'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en '
    }
    response = requests.get(url, headers=headers)
    body = etree.HTML(response.text)
    basic_file_url = 'http://www.ket.com/cm/fileDownMan.ket?attcFilSn='
    xpath_pdf = body.xpath('//*[@id="container"]/div[3]/div[1]/dl/dd[2]/div[2]/span/a/@href')
    xpath_file = body.xpath('//*[@id="container"]/div[3]/div[1]/dl/dd[2]/div[2]/span/a/@filesn')
    product_type = body.xpath('//*[@id="container"]/div[3]/div[1]/dl/dd[2]/div[2]/span/a/text()')
    partn = url.split('=')[1]
    pool = ThreadPool(processes=4)

    xpath_file_queue = queue.Queue()
    for n in range(len(xpath_file)):
        xpath_file_queue.put(xpath_file[n])

    for i in range(len(product_type)):
        if xpath_pdf[i] != '#':
            pdf_url = 'http://www.ket.com/' + str(xpath_pdf[i])
            dic = {product_type[i]: pdf_url}
            pool.apply_async(persistance.add_data, (partn, dic))
        else:
            file_url = basic_file_url + str(xpath_file_queue.get())
            dic = {product_type[i]: file_url}
            pool.apply_async(persistance.add_data, (partn, dic))

    pool.close()
    pool.join()


def requests_post(data):
    response = requests.post(Config.ROOT_URL, data=data, headers=Config.headers_root)
    parser_json(response.text)


def request_detail():
    while not Q.empty():
        # 构造产品详情页的url
        url = Config.DETAIL_URL + Q.get()
        t = threading.Thread(target=test(url,))
        t.start()
    get_page()


global total_row
global count
count = 1


def parser_json(response):
    loads = json.loads(response)
    # 拿到产品总数
    global total_row
    total_row = loads['result']['searchInfo']['totalRow']
    # 拿到产品型号
    lists = loads['result']['list']
    for i in range(len(lists)):
        partnumber = lists[i]['PARTNUMBER']

        if partnumber is None:
            if count < 3:
                data = get_category_cd(count)
                requests_post(data)
            else:
                data = get_category(count)
                requests_post(data)
        else:
            global count
            count = 1
            Q.put(partnumber)
    request_detail()

# 构造最上一级种类集合
total_category = set()
total_category_list = ['A', 'B', 'C', 'd', 'E', 'D', 'H']
for i in range(len(total_category_list)):
    total_category.add(total_category_list[i])


# 获取最上一级的大种类url编号
def get_category(count):
    data = create_data()
    category = data['categoryCd']
    category_list = list(category)
    if total_category is None:
        return
    current_category = total_category.pop()
    category_list[1] = current_category
    count += 1
    category = "".join(category_list)
    data['categoryCd'] = category
    return data


# 获取大分类下小种类url编号
def get_category_cd(count):
    data = create_data()
    categorycd = data['categoryCd']
    category_cd_list = list(categorycd)
    n = int(category_cd_list[3])
    n += 1
    category_cd_list[3] = str(n)
    count += 1
    category = "".join(category_cd_list)
    data['categoryCd'] = category
    print(data)
    return data


if __name__ == '__main__':
    response = requests.post(Config.ROOT_URL, data=create_data(), headers=Config.headers_root)
    parser_json(response.text)


