#!/usr/bin/python3
#coding=utf-8


'''
python+selenium测试框架
'''

import os
import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

import xml
# import xml.etree.ElementTree as ET
# from defusedxml.ElementTree import parse
import defusedxml.ElementTree as ET

import my_log

class my_frame():
    browser = None

    def __init__(self):
        my_log.init_log()

    def quit(self):
        self.browser.quit()


    def get_head(self, root):
        if root == None:
            return

        # 浏览器类型
        browser_type = root.find("Browser")
        if browser_type.text.lower() == "chrome":
            self.browser = webdriver.Chrome()
        else:
            self.browser = webdriver.Firefox(executable_path=r'geckodriver')

        # 测试用例编号
        case_id = root.find("CaseId")
        my_log.log("{0}\n测试用例：{1}".format(
            "*"*60, case_id.text))

        # 产品
        case_id = root.find("Product")
        my_log.log("产品：{0}".format(case_id.text))

        # 模块
        case_id = root.find("Module")
        my_log.log("模块：{0}".format(case_id.text))

    def tpl_openurl(self, node):
        '''
        处理tpl_openurl模板
        在浏览器中打开<url>url</url>
        :param node: <step></step>结点
        :return:
        '''
        for i in node:
            if i.tag.lower() == "url":
                self.browser.get(i.text)
                break

    def tpl_input(self, node):
        '''
        处理tpl_input模板
        按照<ByWhere>指定的xpath定位到文本框；
        将<Args>指定的参数输入到该文本框
        :param node: <step></step>结点
        :return:
        '''
        by = None
        bywhere = None
        args = None

        for i in node:
            if i.tag.lower() == "by" and \
                    i.text.lower() == "xpath":
                by = "xpath"
            if i.tag.lower() == "bywhere":
                bywhere = i.text
            if i.tag.lower() == "args":
                args = i.text
        if by is not None and \
            bywhere is not None and \
            args is not None:
            self.browser.find_element_by_xpath(
                bywhere).send_keys(args)

    def tpl_submit(self, node):
        '''
        处理tpl_submit模板
        按照<ByWhere>指定的xpath定位到“提交”按钮，click；
        :param node: <step></step>结点
        :return:
        '''
        by = None
        bywhere = None

        for i in node:
            if i.tag.lower() == "by" and \
                    i.text.lower() == "xpath":
                by = "xpath"
            if i.tag.lower() == "bywhere":
                bywhere = i.text
        if by is not None and \
                bywhere is not None:
            self.browser.find_element_by_xpath(
                bywhere).send_keys(Keys.ENTER)

    def tpl_check(self, node):
        '''
        处理tpl_check模板
        按照<ByWhere>指定的xpath定位到文本，
        与<Args>指定的参数相同，则成功。
        :param node: <step></step>结点
        :return: 成功返回0
        '''
        by = None
        bywhere = None
        action = None
        args = None
        ret = -1

        for i in node:
            if i.tag.lower() == "by" and \
                    i.text.lower() == "xpath":
                by = "xpath"
            if i.tag.lower() == "bywhere":
                bywhere = i.text
            if i.tag.lower() == "action" and \
                    i.text.lower() == "check":
                action = i.text
            if i.tag.lower() == "args":
                args = i.text

        if by is not None and \
                bywhere is not None and \
                action is not None and \
                args is not None:
            elem = self.browser.find_element_by_xpath(
                bywhere)
            if elem.text.lower() == args:
                ret = 0

        if ret == 0:
            my_log.log("执行成功。")
        else:
            my_log.log("执行失败！")

        return ret


    def get_steps(self, step):
        for node in step:
            for i in node:
                print(i.tag, i.text)

                # 处理tpl_openurl模板
                if i.tag.lower() == "templateid" and \
                        i.text.lower() == "tpl_openurl":
                    self.tpl_openurl(node)
                    break

                # 处理tpl_input模板
                if i.tag.lower() == "templateid" and \
                        i.text.lower() == "tpl_input":
                    self.tpl_input(node)
                    break

                # 处理tpl_submit模板
                if i.tag.lower() == "templateid" and \
                        i.text.lower() == "tpl_submit":
                    self.tpl_submit(node)
                    break

                # 处理tpl_check模板
                # todo: firefox，单步成功，运行失败。问题待查。
                if i.tag.lower() == "templateid" and \
                        i.text.lower() == "tpl_check":
                    self.tpl_check(node)
                    break


    def exec_tc(self, xmlfile):
        ret = False
        try:
            tree = ET.parse(xmlfile)
            root = tree.getroot()
            self.get_head(root)
            self.get_steps(root.iter("Step"))

            time.sleep(2)

            ret = True
        except (EnvironmentError,
                xml.parsers.expat.ExpatError) as err:
            my_log.log("{0}:import error: {1}".format(
                os.path.basename(sys.argv[0]), err))
        finally:
            return ret






class my_location():
    '''
    页面元素定位器
    '''
    pass



class xml_parse():
    '''
    xml解析
    '''
    pass



if __name__ == "__main__":
    fr = my_frame()

    ret = fr.exec_tc(r"./case.xml")

    fr.quit()

    print(ret)

