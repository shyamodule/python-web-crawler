import re
import pymongo.errors
from datetime import datetime
from bs4 import BeautifulSoup
from cfg import config
from urllib.parse import urljoin


limit = config['database_limit']


def html_work(response, collection):
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