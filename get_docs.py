from cfg import config
from datetime import datetime

def get_docs(collection):

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