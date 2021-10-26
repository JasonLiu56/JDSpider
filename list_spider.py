# 爬虫列表页
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree
from proxy import get_html, get_random_ua
from settings import logger


pool = ThreadPoolExecutor(max_workers=4)

# 判断评论数是否合格
pattern = re.compile('(\\d+万+)|(\\d{3,}\\+)')


# 加载name,url列表
def load_name_url():
    name_url_list = []
    with open('./name_url.txt', 'r', encoding='utf-8') as fr:
        for line in fr.readlines():
            name, url = line.strip().split('\t')
            name = name[5:]
            url = url[4:]
            name_url_list.append((name, url))
        return name_url_list


# 请求和解析函数
def request_and_parse(url, category, i):
    try:
        logger.info("爬取分类:{}\t第{}页".format(category, i))
        text = get_html(url.format(i), headers=get_random_ua())
        html_tree = etree.HTML(text)
        product_list = html_tree.xpath('//li[@data-sku]/div[@class="gl-i-wrap"]')  # 获取商品列表
        id_title_list = []
        for product in product_list:
            id = product.xpath('./div[@class="p-name p-name-type-3"]/a/i/@id')[0].split('_')[-1]
            title = ''.join(product.xpath('./div[@class="p-name p-name-type-3"]/a/em/text()'))
            id_title_list.append((id, title))
        return id_title_list
    except:
        logger.info("爬取分类:{}\t第{}页出错".format(category, i))
        return None


# 爬取每一个分类
def crawl_by_category(name_url):
    # 默认爬取100页
    name, url = name_url
    name = re.sub('/','&', name)
    logger.info("开始爬取分类:{}".format(name))
    url += '&psort=4&page={}'
    with open('./category/{}.txt'.format(name), 'w', encoding='utf-8') as fw:
        future_list = []
        for i in range(1, 100):
            future = pool.submit(request_and_parse, url, name, i)
            future_list.append(future)

        all_id_title_list = []
        for id_title_list_future in as_completed(future_list):
            id_title_list = id_title_list_future.result()
            if id_title_list is not None:
                all_id_title_list.extend(id_title_list)

        index = 0
        for id_, title in all_id_title_list:
            if id_ is None or title is None:
                logger.info("错误数据index:{}".format(index))
            else:
                fw.write('{}\t{}\n'.format(id_.strip(), title.strip()))


if __name__ == '__main__':
    name_url_list = load_name_url()
    for name_url in name_url_list:
        crawl_by_category(name_url)