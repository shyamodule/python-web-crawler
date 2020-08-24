import re
import requests
import string
import random
import pymongo
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from cfg import config
from logger import logger
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin


#connecting to mongoDB Atlas
#replace the SRV, my_database, my_collection
client = pymongo.MongoClient("mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]")
db = client.my_database
collection = db.my_collection
logger.debug('Database connected successfully!!')

#creating unique id for every document and ensuring only unique links gets exported to database
collection.create_index([("link", pymongo.ASCENDING)], unique= True)


#getting configuration data
html_dir = config['html_dir']
media_dir = config['media_dir']
size = config['media_size']
sleep_seconds = config['sleep_time']
limit = config['data_limit']
root = config['root']

logger.debug('All configurable variables succesfully installed')


def get_docs():

    now = datetime.now()
    time_threshold = now - config['subtract']

    #getting link from database that is not crawled in last 24 hours(default)
    doc_cursor =   collection.find({'$or' : [
        {'last_crawled_date': None}, 
        {'last_crawled_date': {'$lt': time_threshold}}] 
    })
    doc_list = []
    for _ in range(5):
        try:
            doc_list.append(doc_cursor.next())
        except:
            continue

    return doc_list
    
def save_files(response, filepath):
    ctype = response.headers['content-type']
    enc = response.encoding
    is_media = False
    if 'text' not in ctype:
        is_media = True

    #saving file
    if filepath == None:
        
        result = ''.join(random.choices(string.ascii_letters + string.digits, k = 10))#'k' restricts no. of letters in filename

        if is_media:
            curr_url = response.url
            ext = curr_url.split('.')[-1]
            filename = str(result) + '.' + ext
            filepath = media_dir + filename
            response.raw.decode_content = True
            f = open(filepath, 'wb')
            f.write(response.content)
            f.close()
            logger.debug('Media file is saved in {} directory'.format(media_dir))


        else:
            filename = str(result) + '.' + 'html'
            filepath = html_dir + filename
            f = open(filepath, 'w', encoding=enc)
            f.write(response.text)
            f.close()
            logger.debug('saving html page source into {} directory'.format(html_dir))

    #updating file
    else:
        if is_media:
            response.raw.decode_content = True
            f =  open(filepath, 'wb')
            f.write(response.content)
            f.close()
            
        else:
            f = open(filepath, 'r+', encoding=enc)
            f.write(response.text)
            f.close()
    return filepath

def html_work(response):
    peak = False
    curr_url = response.url
    s= response.text
    html = BeautifulSoup(s, 'html.parser')
    all_atags = html.find_all('a', href=True)
    for link in all_atags:
        link = link.get('href')
        if len(link) < 2:
            continue
        final_link = urljoin(curr_url, link)
        final_link = re.sub('#.*$','',final_link) # to truncate internal reference links
        if 'http' not in final_link:
            continue
        

        post = {
            'link': final_link,
            'source_link': curr_url,
            'is_crawled': False,
            'last_crawled_date': None,
            'response_status': None,
            'content_type': None,
            'content_length': None,
            'created_at': datetime.now(),
            'file_path': None
        }

        
        try:
            collection.insert_one(post)
            if collection.count_documents({}) >= limit:
                peak = True
                break

        except pymongo.errors.DuplicateKeyError:
            continue

    return peak

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
    peak = html_work(response)
    
    logger.debug('Database updated with links from current url: ' + curr_url)

    #database limit
    if peak == True:
        logger.info('Maximum limit reached')
        return True
    


    #saving or updating files
    filepath = doc['file_path']
    f_path_new = save_files(response, filepath)

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
    docs =  get_docs()
    if docs == []:
        return 'All links scrawled!'

    done = False
    with ThreadPoolExecutor() as executor:
        for doc in docs:
            threads.append(executor.submit(scrap_link, doc))

    for task in as_completed(threads, timeout = 30):
        is_completed = task.result(timeout = 30)
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


final_call = None

while(True):
    done =  runner()
    if done:
        final_call = done
        break

    time.sleep(sleep_seconds)


client.close()

if final_call == True:
    while(True):
        print('Maximum limit reached')
        time.sleep(sleep_seconds)

else:
    print(final_call)


