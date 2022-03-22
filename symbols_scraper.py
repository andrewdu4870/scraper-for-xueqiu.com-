import requests
import logging
import time
from fake_useragent import UserAgent
from datetime import datetime

#from tqdm.notebook import tqdm #如果用jupyter则从这里导入
from tqdm import tqdm, trange

# 不可更改部分
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
SYMBOL_URL = 'https://xueqiu.com/service/v5/stock/screener/quote/list?page={page}&size=90&order=desc&orderby=percent&order_by=percent&market=CN&type=sh_sz&_={timestamp}'

maxPage=53

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

headers = make_headers(cookie_path='cookie.txt')

def scrape_api(url):
  # 根据url爬取网页，是最基础的函数
  try:
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.json()
  except requests.RequestException:
    logging.error('error occurred while scraping %s', url, exc_info=True)

def scrape_symbol():
  with open('symbols.txt','a') as f:
    for page in trange(1,maxPage+1):
      url = SYMBOL_URL.format(page=page,timestamp=int(time.mktime(datetime.now().timetuple())))
      index_data = scrape_api(url)
      for data in index_data['data']['list']:
        f.write(data['symbol']+'\n')
      time.sleep(1)

if __name__ == '__main__':
  scrape_symbol()
  print('OK')
