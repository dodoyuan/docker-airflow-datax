import time
import os


def get_format_time():
    '''
    :return:
    '''
    now = time.time()
    tl = time.localtime(now)
    format_time = time.strftime("%Y-%m-%d", tl)
    return format_time


def write_file(filepath, content, filename):
    filename += '.log'
    path = os.path.join(filepath, filename)
    with open(path, 'a+') as f:
        f.write(content)
        f.write('\n')