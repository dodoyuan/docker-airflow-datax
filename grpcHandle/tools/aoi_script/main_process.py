#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(C) 2018 CloudIn.Inc. All right reserved.
# @Author  : YuanQijie
# @Brief   : 读取离线CSV数据, 进行相应处理后格式化写入到pieces表和defects表

from sqlalchemy import create_engine
import logging
import sys
import pandas as pd
import zipfile
import subprocess
import traceback
import os
from argparse import ArgumentParser
import time

# MYSQL_USER = 'root'
# MYSQL_DB = 'aoi_process'
# MYSQL_PWD = 'Rtsecret'
# MYSQL_ADR = '10.232.70.203'
# MYSQL_PORT = '30001'

# MYSQL_USER = 'root'
# MYSQL_DB = 'aspen_cockpit'
# MYSQL_PWD = 'yuan940110'
# MYSQL_ADR = '127.0.0.1'
# MYSQL_PORT = '3306'

logformat = '%(asctime)s | %(filename)s | %(lineno)3d | ' \
            '%(threadName)s | %(levelname)s | %(message)s'
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format=logformat)

LOG = logging.getLogger(__name__)


class MainHandle(object):
    '''
    1. 读取CSV header文件，写表 pieces_process3
    2. 读取 defectlist.csv文件，写入defects_process3表
    '''
    def __init__(self, args):
        self.args = args
        self.engine = create_engine('mysql+mysqldb://%s:%s@%s:%s/%s?'
                       'charset=utf8' % (
                           args.user, args.password, args.host,
                           args.port, args.mysqldb),
                       echo=False, pool_recycle=30, encoding='utf-8')
        self.piece_process_table = 'pieces_process3'
        self.defect_process_table = 'defects_process3'
        # flag, 开启数据调试
        self.output_csv = False

    def _generate_file(self, basepath):
        '''
        生成两个文件，记录已经处理的信息。避免重复处理
        '''
        # 记录已经解压的文件信息
        zipdone = os.path.join(basepath, 'zipdone.txt')
        if not os.path.exists(zipdone):
            file = open(zipdone, 'w')
            file.close()
        # 记录已经处理的 pieces信息
        done = os.path.join(basepath, 'done.txt')
        if not os.path.exists(done):
            file = open(done, 'w')
            file.close()

    def work(self, home_path):
        # 得到系统pieceid
        df = pd.read_sql('select max(pieceid) as max_id from pieces_process3;',
                         self.engine)
        # print(df)
        pieceid = (df['max_id'][0] if df['max_id'][0] else 0) + 1
        LOG.debug("get max pieceid: %d", pieceid)
        self._generate_file(home_path)
        # 解压文件并得到指定文件夹下所有合法未处理文件
        file_names = self.get_file_path(home_path)
        length, count = len(file_names) * 2, 0
        handle_success = []
        for file_name in file_names:
            # 名字合法性问题，对ModularStandardReport-1KSPVA0723-02 (2) 名字后续处理出错
            if file_name.endswith('(2)'):
                file_name = self.file_rename(home_path, file_name)
            count += 1
            dir_path = os.path.join(home_path, file_name)
            header_path = os.path.join(dir_path, 'header.csv')
            LOG.debug("handle  %s/header.csv, %d / %d", file_name, count, length)
            count += 1
            # 读取 header.csv
            data_list = self.read_header_csv(header_path)
            data_dict = self.list_to_dict(pieceid, data_list)
            # 将数据写入到pieces_process表, 如果成功，继续处理defect表。 TODO：两个操作，保证一致性
            if self.write_to_pieces_process(data_dict, self.piece_process_table):
                # 处理 defectlist.csv 文件
                defectslist_path = os.path.join(dir_path, 'defectlist.csv')
                LOG.debug("handle  %s/defectlist.csv, %d / %d", file_name, count, length)
                # aoi_no = data_dict['aoi_no'][0]
                if self.read_defectlist_file_and_write(defectslist_path, pieceid, self.defect_process_table):
                    handle_success.append(file_name)
                    # 处理成功，删除文件夹
                    cmd = 'rm -r {file}'.format(file=dir_path)
                    try:
                        LOG.debug("exc command: %s", cmd)
                        # subprocess.check_output(cmd, shell=True)
                    except Exception as e:
                        traceback.print_exc()
                pieceid += 1
            else:
                pass
        if handle_success:
            done_file_path = os.path.join(home_path, 'done.txt')
            self.write_done_set(handle_success, done_file_path)

    def file_rename(self, home_path, name):
        file_path = os.path.join(home_path, name)
        new_name = name[:-4] + '_2'
        new_file_path = os.path.join(home_path, new_name)
        try:
            LOG.debug("rename file %s to %s", name, new_name)
            os.rename(file_path, new_file_path)
        except Exception as e:
            traceback.print_exc()
        return new_name

    def get_file_path(self, basepath):
        '''
        1. 解压该文件夹下的zip文件
        2. 取出未处理的合法文件
        避免重复处理： 1） zipdone.txt文件    2）done.txt文件
        '''
        self._unzip_file(basepath)
        chose_file = []
        readdirs = [f for f in os.listdir(basepath) if not os.path.isfile(os.path.join(basepath, f)) and not f.startswith('.')]
        # 处理的文件会写在当前目录的done.txt文件中
        donefile_path = os.path.join(basepath, 'done.txt')
        doneset = self.get_done_set(donefile_path)
        for dir in readdirs:
            if dir in doneset:
                continue
            chose_file.append(dir)
        LOG.debug('files to process: %s, total %d', str(chose_file), len(chose_file))
        return chose_file

    def _unzip_file(self, basepath):
        '''
        将指定文件夹下所有zip文件解压,并记录，避免下次重复处理
        '''

        zip_file = [file for file in os.listdir(basepath) if file.endswith('.zip')]
        zip_donefile_path = os.path.join(basepath, 'zipdone.txt')
        doneset = self.get_done_set(zip_donefile_path)
        handled = []
        for file in zip_file:
            if file not in doneset:
                file_path = os.path.join(basepath, file)
                # print('filepath', file_path)
                file_handel = zipfile.ZipFile(file_path)
                for name in file_handel.namelist():
                    file_handel.extract(name, basepath)  # 解压文件还是在当前目录下
                file_handel.close()
                handled.append(file)
                # 解压成功，删除压缩文件
                cmd = 'rm {file}'.format(file=file_path)
                try:
                    LOG.debug("exc command: %s", cmd)
                    subprocess.check_output(cmd, shell=True)
                except Exception as e:
                    traceback.print_exc()
        if handled:
            self.write_done_set(handled, zip_donefile_path)

    def read_header_csv(self, path):
        '''
        返回格式为：['Roll:', '1KSPSA18071841', 'Roll Start:', '2018-07-19 02:02:29', 'Job:', '1KSPSA180718',
        'Report Creation Date:', '2018-07-19 10:02:45'  ... ]
        '''
        fp = open(path, 'r')
        df = pd.read_csv(fp, header=None, sep=';')
        res = []
        for index, row in df.iterrows():
            for i in range(0, 6):
                res.append(row[i])
        return res

    def list_to_dict(self, pieceid, data_list):
        '''

        :return:
        '''
        data_dict = dict()
        data_dict['pieceid'] = [pieceid]
        for i, data in enumerate(data_list):
            if data == 'Roll:':
                data_dict['aoi_no'] = [data_list[i+1]]
            elif data == 'Inspected Width:':
                data_dict['inspected_width'] = [self._data_chansfore(data_list[i+1])]
            elif data == 'Inspected Length:':
                data_dict['inspected_length'] = [self._data_chansfore(data_list[i+1])]
            elif data == 'Material Width:':
                data_dict['material_width'] = [self._data_chansfore(data_list[i+1])]
            elif data == 'Run Length:':
                data_dict['run_length'] = [self._data_chansfore(data_list[i+1])]
            elif data == 'Recipe:':
                data_dict['recipe'] = [self._data_chansfore(data_list[i+1])]
            elif data == 'Roll Stop:':
                data_dict['stop_time'] = [self._data_chansfore(data_list[i+1])]
            elif data == 'Roll Start:':
                data_dict['start_time'] = [self._data_chansfore(data_list[i+1])]
            elif data == 'Comment:':
                data_dict['comment'] = [self._data_chansfore(data_list[i+1])]
            # 少ratio和piecesid数据
        return data_dict

    def _data_chansfore(self, string):
        if isinstance(string, str) and string.endswith('mm'):
            return float(string[:-3])
        # string = str(string).rstrip(' mm')
        # print('---> %s', string)
        return string

    def write_to_pieces_process(self, data_dict, table):
        '''

        :param data_dict:
        :return:
        '''
        # 构造dataframe
        df = pd.DataFrame(data_dict)

        if self.output_csv:
            file_path = '/Users/cloudin/Desktop/process_output_{id}.csv'.format(id=data_dict['pieceid'][0])
            df.to_csv(file_path, index=False)
        try:
            df.to_sql(table, con=self.engine, if_exists='append', index=False, index_label=False, chunksize=256)
            LOG.debug("write to table pieces_process3 sucessful, pieces info: %s", data_dict['aoi_no'][0])
        except Exception as e:
            LOG.debug("write to table pieces_process3 failed, pieces info: %s", data_dict['aoi_no'][0])
            traceback.print_exc()
            return False
        return True

    def read_defectlist_file_and_write(self, path, pieceid, table):
        '''
        读取文件
        映射关系：
        defectid - Defect ID
        defectindex    #kong
        aoi_no - <header.csv>
        defectclass - Defect Class
        severity -  Severity
        severitygroup - # kong
        length -  length [mm]
        width -  width [mm]
        size -   size [mm]
        cdabspos - cdAbsBoxCenter [mm]
        cdpos - cdBoxCenter [mm]
        mdabspos - mdAbsBoxCenter [mm]
        mdpos - mdBoxCenter [mm]
        time - Time
        :return:
        '''
        fp = open(path, 'r')
        df = pd.read_csv(fp, sep=';', low_memory=False,
                         usecols=['Defect ID', 'Defect Class', 'Severity', 'length [mm]', 'width [mm]', 'size [mm]',
                                               'cdAbsBoxCenter [mm]', 'cdBoxCenter [mm]', 'mdAbsBoxCenter [mm]',
                                               'mdBoxCenter [mm]', 'Time'])
        # df.to_csv('/Users/cloudin/Desktop/output2.csv', index=False)
        # 调整对应列名, df.columns 方法需要保证原始数据顺序
        df.columns = ['defectid', 'defectclass', 'severity', 'cdabspos', 'cdpos', 'length',
                      'mdabspos', 'mdpos', 'size', 'width', 'time']

        # 增加一列
        # df['aoi_no'] = aoi_no
        df['pieceid'] = pieceid
        df.replace('-', 0, inplace=True)   # 将数据中不合法数据替换
        if self.output_csv:
            file_path = '/Users/cloudin/Desktop/defects_output_{id}.csv'.format(id=pieceid)
            df.to_csv(file_path, index=False)
        try:
            df.to_sql(table, con=self.engine, if_exists='append', index=False, index_label=False, chunksize=256)
            LOG.debug("write to table %s sucessful", table)
        except Exception as e:
            LOG.debug("write to table %s failed", table)
            traceback.print_exc()
            return False
        return True

    def get_done_set(self, filepath):
        '''
         返回一个set
        :return:
        '''
        name_set = set()
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                # 保证一行一个数据
                data = line.split('\n')[0]
                name_set.add(data)
        # LOG.debug("read total %s aoi_no from file", len(name_set))
        return name_set

    def write_done_set(self, new_list, filepath):
        with open(filepath, 'a') as f:
            for aoi_no in new_list:
                f.writelines(aoi_no)
                f.write('\n')
        LOG.debug("write info successful to done.txt ")

    def run(self):
        day_list = []
        if self.args.oneday:
            now = time.time()
            day_before = now - 24 * 60 * 60
            t2 = time.localtime(day_before)
            day_info = time.strftime("%Y/%m/%d", t2)
            day_list.append(day_info)
        else:
            day_list.extend(self.args.days)

        home_path = self.args.home_dir
        for data_type in ['pva', 'psa']:
            for day in day_list:
                abs_path = os.path.join(home_path, data_type, day)
                handle.work(abs_path)


if __name__ == '__main__':
    try:
        parser = ArgumentParser()
        parser.add_argument('--user',
                            type=str,
                            default='root',
                            help='user to access database')
        parser.add_argument('--password',
                            type=str,
                            default='Rtsecret',
                            help='the password to access database')
        parser.add_argument('--host',
                            type=str,
                            default='10.232.70.203',
                            help='the host which database exist')
        parser.add_argument('--port',
                            type=int,
                            default=30001,
                            help='port to access mysql')
        parser.add_argument('--mysqldb',
                            type=str,
                            default='aoi_process',
                            help='database to use')
        parser.add_argument('--oneday',
                            type=bool,
                            default=False,
                            help='just handle files of last day')
        parser.add_argument('--days',
                            type=list,
                            default=['2018/07/25'],
                            help="specify the days want to handle, like ['2018/07/22','2018/07/22']")
        parser.add_argument('--home_dir',
                            type=str,
                            default='/home/jump-openstack/yqj/ftp',
                            help='specify the home dir')

        args = parser.parse_args()
        handle = MainHandle(args)
        handle.run()
    except Exception:
        message = traceback.format_exc()
        LOG.debug(message)


