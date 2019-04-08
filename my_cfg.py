#!/usr/bin/python3
#coding=utf-8

import os
import configparser

class my_config:
    '''
    获取配置
    '''

    def __init__(self, cfg_file=r"./test_frame.ini"):
        '''
        读取配置文件
        :param cfg_file:
        '''
        if os.path.exists(cfg_file):
            self.get_config(cfg_file)
        else:
            print("读取配置文件[%s]失败。" % cfg_file)

    def get_config(self, cfg_file=r"./test_frame.ini"):
        '''
        自省配置文件，自动添加类的属性
        :param cfg_file: 配置文件名
        :return:
        '''
        self.config = configparser.ConfigParser()
        self.config.read(cfg_file)
        sections = self.config.sections()

        for sec in sections:
            opts = self.config.options(sec)
            for opt in opts:
                setattr(self, opt, self.config[sec][opt])


        #
        #
        # self.root_path = config['COMMON']['root_path']
        # self.log_file = config['COMMON']['log_file']
        # self.tmp_image_file = config['COMMON']['tmp_image_file']
        # self.jym_image_file = config['COMMON']['jym_image_file']
        #
        # self.baidu_app_id = config['BAIDU_APP']['APP_ID']
        # self.baidu_api_key = config['BAIDU_APP']['API_KEY']
        # self.baidu_secret_key = config['BAIDU_APP']['SECRET_KEY']

    def set_config(self, sec, opt, value, cfg_file=r"./test_frame.ini"):
        self.config[sec] = {}
        self.config[sec][opt] = value
        with open(cfg_file, 'w') as f:
            self.config.write(f)
