# python-web-crawler
This is a simple python web-crawler.

This code uses: 
 - beautifulsoup4 4.9.1
 - python3 3.8.5
 - requests 2.24.0 module for HTTP GET requests
 - pymongo 3.11.0 module for interacting with mongoDB
 - concurrent.futures module for multithreading
 
This webcrawler uses MongoDB database.
The link which is crawled will save a copy of its html-source with a random name
All the links are inserted in following form:
 
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
        
        
you can customize:
  - Root URL(from where to start crawling)
  - sleep time between two cycles of crawling
  - database limit
  - directories in which html and other media files will be stored
