import requests
import logging
from fake_useragent import UserAgent
from datetime import datetime
from datetime import timedelta
#from tqdm.notebook import tqdm #如果用jupyter则从这里导入
from tqdm import tqdm
import pymongo
import datetime, time

# 不可更改部分
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
DATA_URL = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={symbol}&begin={begin}&end={end}&period=day&type=before&indicator=kline'
client = pymongo.MongoClient(host='localhost',port=27017)
#client.list_database_names() #查看已有的数据库
db = client.test
#db.list_collection_names() #查看已有的集合
db.list_collection_names()
collection = db.comments

# 可更改部分
years = 3 # 选取数据的时间跨度，整数
eduSHcode=['SH600880','SZ002261','SZ300282',
'SZ300359','SZ300010','SZ300192','SZ002659',
'SH600636','SZ300688','SZ300338','SH603377',
'SZ002621','SH605098','SZ003032','SZ002841',
'SH600661','SH600730','SZ002638','SZ002607',
'SZ300089','SZ000526'] # 股票代码

# 时间戳
now = datetime.datetime.now()
end = int(time.mktime(now.timetuple()))*1000 # *1000 是从毫秒变微妙
three_years_ago = now - datetime.timedelta(days=365*years)
begin = int(time.mktime(three_years_ago.timetuple()))*1000


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

def scrape_num_symbol(symbol):
  # 爬取股票数据
  url = DATA_URL.format(symbol=symbol,begin=begin,end=end) # 将url中空缺的信息填上
  index_data = scrape_api(url)
  return index_data

def save_numdata_mongodb(index_data):
  keys = index_data['data']['column']
  pbar = tqdm(index_data['data']['item'],leave=False)
  for data in pbar:
    pbar.set_description('saving timestamp '+str(data[0]))
    result_data = dict(zip(keys,data))
    collection.insert_one(result_data)

def main():
  pbar = tqdm(eduSHcode) # 进度条
  for symbol in pbar:
    pbar.set_description('Processing '+symbol)
    index_data = scrape_num_symbol(symbol)
    save_numdata_mongodb(index_data)
  print('OK')

if __name__ == '__main__':
    main()
