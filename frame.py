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
import my_exception

class my_frame():
    browser = None

    def __init__(self):
        my_log.init_log()

    def quit(self):
        if self.browser is not None:
            self.browser.quit()

    def proc_except(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_log(exc_type, fname, exc_tb.tb_lineno)
        my_log(e)

    def get_xml_node_text(self, root, tag):
        '''
        从xml中搜索tag，返回其内容；
        若未找到，抛出异常
        :param root:
        :param tag:
        :return:
        '''
        if root == None:
            raise my_exception("异常：输入项为空")
        node = root.find(tag)
        if node is None:
            raise my_exception('异常：不能找到"{0}"标签'.format(tag))
        else:
            return node.text.lower()

    def selenium_input_by_xpath(self, xpath, args):
        '''
        按照xpath搜索页面元素，
        若发现元素，则向其输入args；否则抛出异常。
        :param xpath:
        :param args:
        :return:
        '''
        try:
            self.browser.find_element_by_xpath(
                xpath).send_keys(args)
        except NoSuchElementException as e:
            print(e)
            raise my_exception("异常：未找到{0}".format(xpath))

    def selenium_check_by_xpath(self, xpath, args):
        '''
        按照xpath搜索页面元素，
        若元素文本与args相同，返回True；否则抛出异常。
        :param xpath:
        :param args:
        :return:
        '''
        try:
            elem = self.browser.find_element_by_xpath(xpath)
            if elem.text.lower() == args:
                return True
            else:
                raise my_exception("异常：未找到期望的文本'{0}'".format(args))
        except NoSuchElementException as e:
            print(e)
            raise my_exception("异常：未找到{0}".format(xpath))

    def get_head(self, root):
        try:
            # 浏览器类型
            browser_type = self.get_xml_node_text(root, "Browser")
            if browser_type == "chrome":
                self.browser = webdriver.Chrome()
            else:
                self.browser = webdriver.Firefox(
                    executable_path=r'geckodriver')

            # 测试用例编号
            case_id = self.get_xml_node_text(root, "CaseId")
            my_log.log("{0}\n测试用例：{1}".format(
                "*"*60, case_id))

            # 产品
            product = self.get_xml_node_text(root, "Product")
            my_log.log("产品：{0}".format(product))

            # 模块
            module = self.get_xml_node_text(root, "Module")
            my_log.log("模块：{0}".format(module))

        except my_exception as e:
            self.proc_except(e)


    def tpl_openurl(self, node):
        '''
        处理tpl_openurl模板
        在浏览器中打开<url>url</url>
        :param node: <step></step>结点
        :return:
        '''
        try:
            url = self.get_xml_node_text(node, "url")
            self.browser.get(url)
        except my_exception as e:
            self.proc_except(e)

    def tpl_input(self, node):
        '''
        处理tpl_input模板
        按照<ByWhere>指定的xpath定位到文本框；
        将<Args>指定的参数输入到该文本框
        :param node: <step></step>结点
        :return:
        '''
        try:
            by = self.get_xml_node_text(node, "By")
            bywhere = self.get_xml_node_text(node, "ByWhere")
            args = self.get_xml_node_text(node, "Args")
            if by == "xpath":
                self.selenium_input_by_xpath(bywhere, args)
        except my_exception as e:
            self.proc_except(e)

    def tpl_submit(self, node):
        '''
        处理tpl_submit模板
        按照<ByWhere>指定的xpath定位到“提交”按钮，click；
        :param node: <step></step>结点
        :return:
        '''
        try:
            by = self.get_xml_node_text(node, "By")
            bywhere = self.get_xml_node_text(node, "ByWhere")
            if by == "xpath":
                self.selenium_input_by_xpath(bywhere, Keys.ENTER)
        except my_exception as e:
            self.proc_except(e)

    def tpl_check(self, node):
        '''
        处理tpl_check模板
        按照<ByWhere>指定的xpath定位到文本，
        与<Args>指定的参数相同，则成功。
        :param node: <step></step>结点
        :return: 成功返回True
        '''
        try:
            ret = False
            by = self.get_xml_node_text(node, "By")
            bywhere = self.get_xml_node_text(node, "ByWhere")
            action = self.get_xml_node_text(node, "Action")
            args = self.get_xml_node_text(node, "Args")
            success_info = self.get_xml_node_text(node, "success_info")
            fail_info = self.get_xml_node_text(node, "fail_info")
            if by == "xpath":
                ret = self.selenium_check_by_xpath(bywhere, args)
            if ret == True:
                my_log.log(success_info)
            else:
                my_log.log(fail_info)
            return ret
        except my_exception as e:
            self.proc_except(e)






        # by = None
        # bywhere = None
        # action = None
        # args = None
        # success_info = None
        # fail_info = None
        # ret = False
        #
        # for i in node:
        #     if i.tag.lower() == "by" and \
        #             i.text.lower() == "xpath":
        #         by = "xpath"
        #     if i.tag.lower() == "bywhere":
        #         bywhere = i.text
        #     if i.tag.lower() == "action" and \
        #             i.text.lower() == "check":
        #         action = i.text
        #     if i.tag.lower() == "args":
        #         args = i.text
        #     if i.tag.lower() == "success_info":
        #         success_info = i.text
        #     if i.tag.lower() == "fail_info":
        #         fail_info = i.text
        #
        # if by is not None and \
        #         bywhere is not None and \
        #         action is not None and \
        #         args is not None:
        #     try:
        #         elem = self.browser.find_element_by_xpath(bywhere)
        #         if elem.text.lower() == args:
        #             ret = True
        #     except NoSuchElementException:
        #         pass
        #         # print("except NoSuchElementException")
        #
        # if ret == True:
        #     if success_info is not None:
        #         my_log.log(success_info)
        # else:
        #     if fail_info is not None:
        #         my_log.log(fail_info)
        #
        # return ret


    def get_steps(self, step):
        ret = False
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
                    ret = self.tpl_check(node)
                    break
        return ret


    def exec_tc(self, xmlfile):
        ret = False
        try:
            tree = ET.parse(xmlfile)
            root = tree.getroot()
            self.get_head(root)
            ret = self.get_steps(root.iter("Step"))
            time.sleep(5)
        except (EnvironmentError,
                xml.parsers.expat.ExpatError) as e:
            my_log.log("{0}:import error: {1}".format(
                os.path.basename(sys.argv[0]), e))
        except Exception as e:
            self.proc_except(e)
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
    try:

        fr = my_frame()

        ret = fr.exec_tc(r"./case.xml")

        fr.quit()

        print(ret)

    except Exception as e:
        print(e)

