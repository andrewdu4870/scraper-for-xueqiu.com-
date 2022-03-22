import logging
#from tqdm.notebook import tqdm #如果用jupyter则从这里导入
from tqdm import tqdm
import pymongo
import time
import json

# 不可更改部分
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
client = pymongo.MongoClient(host='localhost',port=27017)
#client.list_database_names() #查看已有的数据库
db = client.test
#db.list_collection_names() #查看已有的集合
collection = db.sh000001

def save_numdata_mongodb(index_data):
  about = index_data['data']['symbol']
  keys = index_data['data']['column']
  pbar = tqdm(index_data['data']['item'],leave=False)
  for data in pbar:
    pbar.set_description('saving timestamp '+str(data[0]))
    result_data = dict(zip(keys,data))
    result_data['symbol'] = about
    result_data['timestamp'] = time.strftime('%Y-%m-%d', time.localtime(result_data['timestamp']/1000))
    collection.insert_one(result_data)

with open('SH000001.json') as f:
  index_data =  json.loads(f.read())
  save_numdata_mongodb(index_data)
