
from datetime import timedelta
config = {
     # after this much time, the scrapping will start from begining
    'subtract': timedelta(days=1, hours=0, minutes=0),

     # path of directory in which all html files will be saved
    'html_dir': 'html_files/',

     # path of direcory in which all other media files will be saved
    'media_dir': 'other_media/',

     # if it is a image, video, audio or application url, then this is the maximum file
     #size in bytes, that will be allowed to download
    'media_size': 4e6, #roughly 4MB

     #sleep time between two cycles
    'sleep_time': 5,

     #max no. of documents to be inserted in database
    'data_limit': 5000,

    'root': 'https://flinkhub.com',

}
