# encoding: utf-8
"""
这个模块用来提供FTP服务
"""

import os
import sys
import ftplib
import traceback
import logging

logformat = '%(asctime)s | %(filename)s | %(lineno)3d | ' \
            '%(threadName)s | %(levelname)s | %(message)s'
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format=logformat)

LOG = logging.getLogger(__name__)

# 获取合法文件可能的后缀
SUFFIX = ['_zip', '(2).zip']

class FtpDownloader(object):
    PATH_TYPE_UNKNOWN = -1
    PATH_TYPE_FILE = 0
    PATH_TYPE_DIR = 1

    def __init__(self, host, user=None, passwd=None, port=21, timeout=30):
        self.conn = ftplib.FTP(
            host=host,
            user=user,
            passwd=passwd,
            timeout=timeout
        )
        self.conn.encoding = 'utf-8'

    def dir(self, *args):
        """
        by defualt, ftplib.FTP.dir() does not return any value.
        Instead, it prints the dir info to the stdout.
        So we re-implement it in FtpDownloader, which is able to return the dir info.
        """
        info = []
        cmd = 'LIST'
        for arg in args:
            if arg:
                cmd = cmd + (' ' + arg)
        self.conn.retrlines(cmd, lambda x: info.append(x.strip().split()))
        return info

    def tree(self, rdir=None, init=True):
        """
        recursively get the tree structure of a directory on FTP Server.
        args:
            rdir - remote direcotry path of the FTP Server.
            init - flag showing whether in a recursion.
        """
        if init and rdir in ('.', None):
            rdir = self.conn.pwd()
        tree = []
        tree.append((rdir, self.PATH_TYPE_DIR))

        dir_info = self.dir(rdir)
        for info in dir_info:
            # info 格式['-r--r--r--', '1', 'ftp', 'ftp', '68855', 'Jul', '24', '01:06',
            # 'DefectListReport-1KSPSA18072345', '(2).zip']
            # 需要注意的是如果最后一个是 (2).zip，名字要拼接
            attr = info[0]  # attribute
            name = info[-1]
            if name == '(2).zip':
                name = info[-2] + ' ' + info[-1]
            path = os.path.join(rdir, name)
            if attr.startswith('-'):
                if any([name.endswith(suf) for suf in SUFFIX]):   # 符合SUFFIX后缀的文件
                    tree.append((path, self.PATH_TYPE_FILE))
            elif attr.startswith('d'):
                if (name == '.' or name == '..'):  # skip . and ..
                    continue
                tree.extend(self.tree(rdir=path, init=False))  # recurse
            else:
                tree.append((path, self.PATH_TYPE_UNKNOWN))

        return tree

    def downloadFile(self, rfile, lfile):
        """
        download a file with path %rfile on a FTP Server and save it to locate
        path %lfile.
        """
        ldir = os.path.dirname(lfile)  # 返回该文件目录
        if not os.path.exists(ldir):
            os.makedirs(ldir)
        f = open(lfile, 'wb')
        self.conn.retrbinary('RETR %s' % rfile, f.write)
        f.close()
        return True

    def treeStat(self, tree):
        numDir = 0
        numFile = 0
        numUnknown = 0
        for path, pathType in tree:
            if pathType == self.PATH_TYPE_DIR:
                numDir += 1
            elif pathType == self.PATH_TYPE_FILE:
                numFile += 1
            elif pathType == self.PATH_TYPE_UNKNOWN:
                numUnknown += 1
        return numDir, numFile, numUnknown

    def downloadDir(self, rdir='.', ldir='.', tree=None,
                    errHandleFunc=None, verbose=True):
        """
        download a direcotry with path %rdir on a FTP Server and save it to
        locate path %ldir.
        args:
            tree - the tree structure return by function FtpDownloader.tree()
            errHandleFunc - error handling function when error happens in
                downloading one file, such as a function that writes a log.
                By default, the error is print to the stdout.
        """
        if not tree:
            tree = self.tree(rdir=rdir, init=True)
        numDir, numFile, numUnknown = self.treeStat(tree)
        LOG.debug("download from FTP server,total files %d", numFile)

        if not os.path.exists(ldir):
            os.makedirs(ldir)
        # 返回规范化的绝对路径
        ldir = os.path.abspath(ldir)

        numDownOk = 0
        numDownErr = 0
        count = 0
        for rpath, pathType in tree:
            lpath = os.path.join(ldir, rpath.strip('/').strip('\\').replace('_zip', '.zip')[2:])
            if ' (2).zip' in lpath:
                temp = lpath.split(' ')
                lpath = temp[0] + '.zip'
            if pathType == self.PATH_TYPE_DIR:
                if not os.path.exists(lpath):
                    os.makedirs(lpath)
            elif pathType == self.PATH_TYPE_FILE:
                count += 1
                # if count == 5:
                #     LOG.debug("file for test,nums ok")
                #     break
                # check file, skip if exist, TODO：上一次外部强行中断会导致文件下载一半，而下次跳过下载，后续处理会出错
                if os.path.exists(lpath):
                    LOG.debug("file %s exist,skip", lpath)
                    continue
                try:
                    self.downloadFile(rpath, lpath)
                    LOG.debug("download file %s %d / %d", rpath, count, numFile)
                    numDownOk += 1
                except Exception as err:
                    numDownErr += 1
                    LOG.warning('An Error occurred when downloading '
                                'remote file %s' % rpath)
                    traceback.print_exc()
            elif pathType == self.PATH_TYPE_UNKNOWN:
                if verbose:
                    LOG.warning('Unknown type romote path got: %s' % rpath)

        return numFile, numDownErr, numDownOk


# if __name__ == '__main__':
#
#     fd = FtpDownloader(
#         host='10.232.1.132',
#         user='cloudin_pva',
#         passwd='cloudin',
#         port=21,
#         timeout=10
#     )
#     numFile, numDownErr, numDownOk = fd.downloadDir(
#         rdir='./2018/07/22',
#         ldir='/Users/cloudin/ftp',
#         tree=None,
#         errHandleFunc=None,
#         verbose=True
#     )
