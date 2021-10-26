# 爬取商品标题及评论
import os
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from proxy import get_html, get_random_ua
from settings import logger


pool = ThreadPoolExecutor(max_workers=6)

# 响应头及url
comment_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1'


# 请求和解析函数
# id为商品id, i为页数
def request_and_parse(id, i):
    return_comments = []
    try:
        logger.info("爬取商品id:{}评论\t第{}页".format(id, i))
        text = get_html(comment_url.format(id, i), headers=get_random_ua())
        res = re.findall('fetchJSON_comment98\((.*?)\);', text, re.S)
        comments = json.loads(res[0], strict=False)
        for comment in comments['comments']:
            # logger.info(comment['content'])
            return_comments.append(comment['content'].strip())
        return return_comments
    except:
        logger.info("爬取商品id:{}评论\t第{}页出错".format(id, i))
        return return_comments


# 获取商品标题及评论
@logger.catch
def get_title_comments(id):
    all_return_comments = []

    # 爬取标题
    logger.info("爬取id:{}的商品评论".format(id))
    # 爬取评论
    future_list = []
    for i in range(40):
        future = pool.submit(request_and_parse, id, i)
        future_list.append(future)

        for return_comments_obj in as_completed(future_list):
            return_comments = return_comments_obj.result()
            if len(return_comments) > 0:
                all_return_comments.extend(return_comments)

    return all_return_comments


# 保存数据
def store_data(category, id, title, return_comments):
    if return_comments is None or len(return_comments) == 0 or len(return_comments) < 200:
        return

    return_comments = list(set(return_comments))
    if not os.path.exists(f'./{category}'):
        os.mkdir(f'./{category}')

    # 保存
    with open(f'./{category}/{id}.txt', 'w', encoding='utf-8') as fw:
        fw.write(title + '\n')
        for return_comment in return_comments:
            fw.write(return_comment + '\n')

    logger.info(f"保存id:{id}\tcategory:{category}")


# 遍历分类列表启动爬虫任务
def crawl_by_category():
    for category_file_name in os.listdir('./category'):
        category = category_file_name.split('.')[0]
        category_file_name = os.path.join('./category', category_file_name)
        with open(category_file_name, 'r', encoding='utf-8') as fr:
            for line in fr.readlines()[:1]:
                items = line.strip().split('\t')
                if len(items) == 2:
                    id, title = items[0], items[1]

                    # 根据商品id爬虫
                    return_comments = get_title_comments(id)
                    # 保存爬虫
                    store_data(category, id, title, return_comments)


if __name__ == '__main__':
    crawl_by_category()