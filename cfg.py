
from datetime import timedelta
config = {

    # mongoDB SRV link
    'srv': "mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]",

    # database name
    'db': 'testdb',

    #collection name
    'coll': 'test',

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
    'sleep': 5,

     #max no. of documents to be inserted in database
    'database_limit': 5000,

    'root': 'https://flinkhub.com',

}
