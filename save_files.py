
import random
import string
from cfg import config
from logger import logger

html_dir = config['html_dir']
media_dir = config['media_dir']


def save_files(response, filepath):
    ctype = response.headers['content-type']
    enc = response.encoding
    is_media = False
    if 'text' not in ctype:
        is_media = True

    #saving file
    if filepath == None:

        result = ''.join(random.choices(string.ascii_letters + string.digits, k = 10))
        #'k' restricts no. of letters in filename
        name =  str(result)

        if is_media:
            curr_url = response.url
            ext = curr_url.split('.')[-1]
            filename = name + '.' + ext
            filepath = media_dir + filename
            response.raw.decode_content = True
            f = open(filepath, 'wb')
            f.write(response.content)
            f.close()
            logger.debug('Media file is saved in {} directory'.format(media_dir))


        else:
            filename = name + '.' + 'html'
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