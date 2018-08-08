#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(C) 2018 CloudIn.Inc. All right reserved.
# @Author  : YuanQijie
# @Brief   :

import os
import time
import logging
import sys
import smtplib
import subprocess
import traceback
from argparse import ArgumentParser
from email.mime.text import MIMEText
from email.header import Header

try:
    from settings import FILE_STROE_PATH, RECEIVE_EMAIL
except ImportError:
    PRO_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
    sys.path.insert(0, PRO_ROOT_PATH)
    from settings import FILE_STROE_PATH, RECEIVE_EMAIL

logformat = '%(asctime)s | %(filename)s | %(lineno)3d | ' \
            '%(threadName)s | %(levelname)s | %(message)s'
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format=logformat)

LOG = logging.getLogger(__name__)


class MysqlDump():
    def __init__(self, args):
        self.args = args

    def run(self):
        database = self.args.database
        path = FILE_STROE_PATH

        old_file = self.dump(database)
        if old_file:
            self.delete_file(path, database, old_file)

    def dump(self, database):
        '''
        执行数据备份
        database: 需要备份的数据库
        '''
        user = self.args.user
        password = self.args.password
        path = FILE_STROE_PATH
        host = self.args.host
        port = self.args.port
        filename, old_filename = self.get_filename()
        dirname = os.path.join(path, '{}_bak/'.format(database))
        file_place = os.path.join(dirname, filename)
        if not os.path.exists(dirname):
            try:
                subprocess.check_output('mkdir -p {}'.format(dirname), shell=True)
                LOG.debug('create dir {}'.format(dirname))
            except Exception as e:
                traceback.print_exc()
                return

        if not os.path.exists(file_place):
            cmd = 'mysqldump -h{host} -P{port} -u{user} -p{passwd} {database} > ' \
                  '{place}'.format(user=user, passwd=password, database=database,
                                   place=file_place, host=host, port=port)
            try:
                LOG.debug("dump %s begin at time %s", database, self.get_time())
                subprocess.check_output(cmd, shell=True)
            except Exception as e:
                message = "dump {database} fail at time {time}".format(database=database, time=self.get_time())
                LOG.debug(message)
                message += traceback.format_exc()
                self.send_email(message)
            else:
                LOG.debug("dump %s success at time %s", database, self.get_time())
            return old_filename
        else:
            LOG.debug('%s already exists', '/'.join(file_place.split('/')[-2:]))
            return None

    def send_email(self, mes):
        '''
        向管理员发送邮件报告执行结果
        '''
        content = '邮件信息: {info}'.format(info=mes)
        sender = 'notify@cloudin.cn'
        receivers = RECEIVE_EMAIL
        mail_user = 'notify@cloudin.cn'
        mail_pass = 'NOTIFYbeb4bd7a'
        message = MIMEText(content, 'plain', 'utf-8')
        message['Subject'] = Header('Mysql dump error message', 'utf-8')
        message['From'] = sender
        message['To'] = receivers
        try:
            smtpObj = smtplib.SMTP()
            mail_host = 'smtp.exmail.qq.com'
            smtpObj.connect(mail_host, 25)
            # smtpObj.login(mail_user, mail_pass)
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            smtpObj.quit()
            LOG.debug('Successfully sent email')
        except smtplib.SMTPException as e:
            LOG.warning('error: %s', e)

    def delete_file(self, path, database, filename):
        '''
        删除七天前数据
        '''
        file = os.path.join(path, '{}_bak/'.format(database), filename)
        if os.path.exists(file):
            # LOG.debug('file %s exists' % filename)
            cmd = 'rm {file}'.format(file=file)
            try:
                subprocess.check_output(cmd, shell=True)
            except Exception as e:
                traceback.print_exc()
                LOG.debug('remove %s failed!' % '/'.join(cmd.split('/')[-2:]))
                return
            LOG.debug('remove %s success!' % '/'.join(cmd.split('/')[-2:]))
        # else:
        #     LOG.debug('%s has no old data to remove', database)

    def get_filename(self):
        '''
        以当前时间为文件名，格式是: 年-月-日.sql
        同时返回具体时间以及七天前文件的文件名
        :return:
        '''
        now = time.time()
        tl = time.localtime(now)
        filename = time.strftime("%Y-%m-%d", tl)
        days = self.args.days

        seven_day_before = now - days * 24 * 60 * 60
        t2 = time.localtime(seven_day_before)
        old_filename = time.strftime("%Y-%m-%d", t2)
        return filename + '.sql', old_filename + '.sql'

    def get_time(self):
        now = time.time()
        tl = time.localtime(now)
        format_str = time.strftime("%Y-%m-%d %H:%M:%S", tl)
        return format_str


if __name__ == '__main__':
    try:
        parser = ArgumentParser()
        parser.add_argument('--database',
                            type=str,
                            default='aspen_wheel',
                            help='the database you want to dump')
        parser.add_argument('--user',
                            type=str,
                            default='root',
                            help='user to access database')
        parser.add_argument('--password',
                            type=str,
                            default='yuan940110',
                            help='the password to access database')
        parser.add_argument('--host',
                            type=str,
                            default='127.0.0.1',
                            help='the host which database exist')
        parser.add_argument('--port',
                            type=int,
                            default=3306,
                            help='port to access mysql')
        # 运行数据保留天数，默认7天
        parser.add_argument('--days',
                            type=int,
                            default=7,
                            help='days want to keep')

        args = parser.parse_args()
        mysqldump = MysqlDump(args)
        mysqldump.run()
    except Exception:
        message = traceback.format_exc()
        LOG.debug(message)
