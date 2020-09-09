# python-web-crawler
Web Crawler goes by many names, including spiders, spybots etc. This web crawler starts crawling links from a ROOT URL. It will upload unique and valid links in MongoDB database. Once all links are crawled on the page, it will save the HTML source code locally, with a random name in user-specified library. Then it will fetch five links from the database which are not crawled is last 24 hours, and these links will be crawled simultaneously. This cycle will be repeated untill program is terminated.

The crawler will not crawl media links, instead it will download media file on that link if its size is less than 2 MB (configurable).

The crawler will sleep for 5 seconds before moving on to the next link.

The default maximum limit of number of documents in MongoDB database is 5000 docs. This means that once Database will have 5000 links, the cycle will not crawl any links untill some links get deleted.

The links will be posted in Database as follows

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
 
This code uses: 
 - beautifulsoup4 4.9.1
 - python3 3.8.5
 - requests 2.24.0 module for HTTP GET requests
 - pymongo 3.11.0 module for interacting with mongoDB
 - concurrent.futures module for multithreading
 
     
        
