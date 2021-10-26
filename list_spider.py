# 爬虫列表页
import re
import time
import random
from lxml import etree
from proxy import get_html, get_random_ua
from settings import logger


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


# 爬取每一个分类
def crawl_by_category(name_url):
    # 默认爬取100页
    name, url = name_url
    name = re.sub('/','&', name)
    logger.info("开始爬取分类:{}".format(name))
    url += '&psort=4&page={}'
    with open('./category/{}.txt'.format(name), 'w', encoding='utf-8') as fw:
        for i in range(1, 100):
            try:
                text = get_html(url.format(i), headers=get_random_ua())
                time.sleep(random.randint(2,6)/10)
                logger.info("爬取分类:{}\t第{}页".format(name, i))
                html_tree = etree.HTML(text)
                product_list = html_tree.xpath('//li[@data-sku]/div[@class="gl-i-wrap"]')   # 获取商品列表
                for product in product_list:
                    id = product.xpath('./div[@class="p-name p-name-type-3"]/a/i/@id')[0].split('_')[-1]
                    title = ''.join(product.xpath('./div[@class="p-name p-name-type-3"]/a/em/text()'))
                    if id is not None and len(id.strip()) > 0:
                        fw.write('{}\t{}\n'.format(id.strip(), title.strip()))
                        # logger.info('{}\t{}'.format(id.strip(), title.strip()))
                    else:
                        logger.info("错误数据id:{}\ttitle:{}".format(id, title))
                fw.flush()
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    name_url_list = load_name_url()
    for name_url in name_url_list:
        crawl_by_category(name_url)