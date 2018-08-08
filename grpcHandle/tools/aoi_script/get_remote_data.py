#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(C) 2018 CloudIn.Inc. All right reserved.
# @Author  : YuanQijie
# @Brief   : 将远程PSA和PVA数据拉取到本地

import sys
import logging
from tools.aoi_script.ftpdownloader import FtpDownloader
import os
import time
import subprocess
import traceback
from argparse import ArgumentParser

logformat = '%(asctime)s | %(filename)s | %(lineno)3d | ' \
            '%(threadName)s | %(levelname)s | %(message)s'
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format=logformat)

LOG = logging.getLogger(__name__)

# FTP登陆信息，两个方式，分别取不同的home目录中数据
FTP_HOST = '10.232.1.132'
FTP_PORT = 21
FTP_USER_PVA = 'cloudin_pva'
FTP_PWD_PVA = 'cloudin'

FTP_USER_PSA = 'cloudin_psa'
FTP_PWD_PSA = 'cloudin'


class FileHandle():
    '''
    连接到Windows FTP server，注意有两个账号：
    cloudin_pva   clouin_psa  分别读取pva和psa 对应目录下的数据
    密码都是 cloudin
    '''
    def __init__(self, args):
        self.args = args

    def download_dir_file(self, fd, down_dir, local_dir):
        """Writer description
           下载down_dir中所有文件到指定目录
        """

        num_file, num_err, num_ok = fd.downloadDir(
            rdir=down_dir,
            ldir=local_dir,
            tree=None,
            errHandleFunc=None,
            verbose=True
        )
        LOG.debug("total files: %d, download ok: %d, download failed: %d", num_file, num_ok, num_err)

    def work(self):
        # 返回目录格式 ['./2018/07/22','./2018/07/23','./2018/07/24',....]
        dir_list = self.get_all_dir()
        # pva
        LOG.debug("start to handle PVA files...")
        pva_fd = FtpDownloader(
            host=FTP_HOST,
            user=FTP_USER_PVA,
            passwd=FTP_PWD_PVA,
            port=FTP_PORT,
        )
        for each_dir in dir_list:
            #  将 each_dir 中所有文件下载到 FTP_DOWNLOAD_PVA_DIR中
            self.download_dir_file(pva_fd, each_dir, self.args.pva_home_path)

        # psa
        LOG.debug("start to handle PSA files...")
        psa_fd = FtpDownloader(
            host=FTP_HOST,
            user=FTP_USER_PSA,
            passwd=FTP_PWD_PSA,
            port=FTP_PORT,
        )
        for each_dir2 in dir_list:
            self.download_dir_file(psa_fd, each_dir2, self.args.psa_home_path)

    def get_all_dir(self, oneday=False):
        '''
        两个功能：1。 返回前一天生成的目录，适用于每日定时任务
                2。 返回指定日期
        '''
        dir_list = []
        if oneday is True:
            now = time.time()
            day_before = now - 24 * 60 * 60
            t2 = time.localtime(day_before)
            day_info = time.strftime("%Y/%m/%d", t2)
            dir_list.append('./'+day_info)
        else:
            # 简化，指定目录
            for day in self.args.days:
                dir_list.append('./'+day)
        return dir_list

    def rename_files(self, home_dir, path):
        '''
        将指定目录下的文件重命名
        '''
        abs_path = os.path.join(home_dir, path)
        files = [f for f in os.listdir(abs_path) if f.endswith('_zip')]
        for file in files:
            old_name = os.path.join(abs_path, file)
            name = file.replace('_zip', '.zip')
            new_name = os.path.join(abs_path, name)
            cmd = 'mv {old} {new}'.format(old=old_name, new=new_name)
            try:
                LOG.debug("exc command: %s", cmd)
                subprocess.check_output(cmd, shell=True)
            except Exception as e:
                traceback.print_exc()


if __name__ == '__main__':
    try:
        parser = ArgumentParser()
        parser.add_argument('--pva_home_path',
                            type=str,
                            default='/home/jump-openstack/yqj/ftp/pva',
                            help='the DIR for pva file download from FTP server')

        parser.add_argument('--psa_home_path',
                            type=str,
                            default='/home/jump-openstack/yqj/ftp/psa',
                            help='the DIR for psa file download from FTP server')
        parser.add_argument('--oneday',
                            type=bool,
                            default=False,
                            help='just handle the file of last day')
        parser.add_argument('--days',
                            type=list,
                            default=['2018/07/25'],
                            help="specify the days want to handle, like ['2018/07/22','2018/07/22']")
        args = parser.parse_args()
        handle = FileHandle(args)
        handle.work()
    except Exception:
        message = traceback.format_exc()
        LOG.debug(message)

