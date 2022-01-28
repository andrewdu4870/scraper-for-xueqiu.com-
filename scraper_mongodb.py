import requests
import logging
from fake_useragent import UserAgent
from datetime import datetime
from datetime import timedelta
#from tqdm.notebook import tqdm #如果用jupyter则从这里导入
from tqdm import tqdm
import pymongo

# 不可更改部分
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
INDEX_URL = 'https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol={symbol}&hl=0&source=user&sort={sort}&page={page}&q=&type=11'
client = pymongo.MongoClient(host='localhost',port=27017)
#client.list_database_names() #查看已有的数据库
db = client.test
#db.list_collection_names() #查看已有的集合
collection = db.comments

# 可更改部分
sort = 'time' # 时间排序
#sort = 'alpha'# 热度排序
eduSHcode=['SH600880','SZ002261','SZ300282',
'SZ300359','SZ300010','SZ300192','SZ002659',
'SH600636','SZ300688','SZ300338','SH603377',
'SZ002621','SH605098','SZ003032','SZ002841',
'SH600661','SH600730','SZ002638','SZ002607',
'SZ300089','SZ000526'] # 股票代码
keys = {'fav_count','hot','id','like_count',
'text','timeBefore','view_count','user_id'} # 需要的数据类型
maxPage=100 # 最大为100


def make_headers(cookie_path='cookie.txt'):
  # 生成HTML请求头
  ua = UserAgent()
  headers = {
  'user-Agent':ua.random,
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="97", "Chromium";v="97"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1'
  }
  with open(cookie_path,"r") as f:
    cookie = f.read()
    headers['cookie'] = cookie
  return(headers)


# 生成HTML请求头
headers = make_headers()

def scrape_api(url):
  # 根据url爬取网页，是最基础的函数
  try:
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.json()
  except requests.RequestException:
    logging.error('error occurred while scraping %s', url, exc_info=True)

def scrape_symbol(symbol):
  # 爬取股票信息
  for page in tqdm(range(1, maxPage + 1), desc='Page',leave=False):
    url = INDEX_URL.format(symbol=symbol, page=page, sort=sort) # 将url中空缺的信息填上
    index_data = scrape_api(url)
    if index_data['list'] == []:
      return
    save_data_mongodb(index_data)

def save_data_mongodb(index_data):
  # 输入为一页十条评论，分别保存
  about = index_data.get('about')
  for comment_data in index_data.get('list'):
    # 先处理时间格式
    if 'timeBefore' in comment_data.keys():
      thetime = str(comment_data['timeBefore'])
      comment_data['timeBefore'] = parse_time(thetime)
    
    # 好像bool值不能直接保存
    if 'hot' in comment_data.keys():
      comment_data['hot'] = str(comment_data['hot'])
    
    # 提取需要的信息
    result_data = {key:value for key,value in comment_data.items() if key in keys }
    result_data['symbol'] = about
    #保存
    collection.insert_one(result_data)

def parse_time(thetime):
  # 此函数抄自： https://github.com/py-bin/xueqiu_spider
  # 稍有修改
  # 处理爬取时间格式异常问题，如“今天 08:30”、“20分钟前”
  date_now = datetime.now()
  if '今天' in thetime:
      rst = thetime.replace('今天',date_now.strftime('%Y-%m-%d'))
  elif '昨天' in thetime:
      the_time = date_now - timedelta(days=1)
      rst = thetime.replace('昨天',the_time.strftime('%Y-%m-%d'))
  elif '分钟前' in thetime:
      the_min = int(thetime[:-3])
      the_time = date_now - timedelta(minutes=the_min)
      rst = the_time.strftime('%Y-%m-%d %H:%M')
  elif '秒前' in thetime:
      rst = date_now.strftime('%Y-%m-%d %H:%M')
  elif len(thetime)== 11:
      rst = str(date_now.year) + '-' + thetime
  else:
      rst = thetime
  return rst

def main():
  pbar = tqdm(eduSHcode) # 进度条
  for symbol in pbar:
    pbar.set_description('Processing '+symbol)
    scrape_symbol(symbol)
  print('OK')

if __name__ == '__main__':
  main()
