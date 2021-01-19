import pymongo
import requests
import time
from cfg import config
from logger import logger
from datetime import datetime
from get_docs import get_docs
from concurrent.futures import ThreadPoolExecutor, as_completed
from html_work import html_work
from save_files import save_files

srv = config['srv']
db = config['db']
coll = config['coll']
root = config['root']
size = config['media_size']
sleep_seconds  = config['sleep']


#connecting to mongoDB Atlas
client = pymongo.MongoClient(srv)
database = client[db]
collection = database[coll]
logger.debug('Database connected successfully!!')

#creating unique id for every document and ensuring only unique links gets exported to database
collection.create_index([("link", pymongo.ASCENDING)], unique= True)




def scrap_link(doc):
    curr_url = doc.get('link')

    logger.debug('Cycle started for url: ' + curr_url)

    #fetching html of current url
    try:
        logger.debug('Making a HTTP get request for: ' + curr_url) 
        header = requests.head(curr_url, timeout = 5)

        clength = header.headers.get('content-length', 0)

        if float(clength) != 0:
            if float(clength) > size:
                collection.update_one({'_id': doc['_id']}, {'$set': {
                    'response': 'File size too big to download',
                    'is_crawled': True,
                    'last_crawled_date': datetime.now()}})
                return
            else:
                response = requests.get(curr_url, timeout = 5)
        
        else:
            response = requests.get(curr_url, timeout = 5)
            clength  = len(response.content)


    except:
        logger.exception('Failed to get HTML source from: ' + curr_url)
        collection.update_one({'_id': doc['_id']}, {'$set': {
            'response': 'Error in getting request',
            'is_crawled': False,
            'last_crawled_date': datetime.now()}})
        return


    #parsing html file to get links present in HTML source
    logger.debug('Parsing HTML and getting urls from the page')

    peak = html_work(response, collection)
    
    logger.debug('Database updated with links from current url: ' + curr_url)

    
    #saving or updating files
    filepath = doc['file_path']
    f_path_new = save_files(response, filepath)
    
    logger.debug('File saved in directory')
    
    
    #database limit
    if peak == True:
        logger.info('Maximum limit reached')
        return True
    



    ctype = response.headers['Content-type']
    status = response.status_code

    collection.update_one({'_id': doc['_id']}, {'$set': {
        'content_length': clength,
        'content_type': ctype,
        'response_status': status,
        'is_crawled': True,
        'last_crawled_date': datetime.now(),
        'file_path': f_path_new
    }})

    logger.debug('Doc updated with response') 



    logger.debug('Cycle over')
    return False

def runner():
    threads= []
    docs =  get_docs(collection)
    if docs == []:
        return 'All links crawled!'

    done = False
    with ThreadPoolExecutor() as executor:
        for doc in docs:
            threads.append(executor.submit(scrap_link, doc))

    for task in as_completed(threads):
        is_completed = task.result()
        if is_completed==True:
            done = True
            break

    return done





if collection.count_documents({}) == 0:
    collection.insert_one({
    'link': root,
    'source_link': 'Root_URL',
    'is_crawled': False,
    'last_crawled_date': None,
    'response_status': None,
    'content_length': None,
    'content_type': None,
    'Created_at': datetime.now(),
    'file_path': None
    })



while(True):
    done =  runner()
    if done == 'All links crawled!':
        print(done)
    elif done == True:
        print('Maximum limit reached')
    time.sleep(sleep_seconds)


client.close()
