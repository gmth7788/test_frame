#!/usr/bin/python3
#coding=utf-8


'''
python+selenium测试框架
'''

import os
import time
import sys

import requests
import pyautogui

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
import my_cfg
import my_exception as EXCP




class my_frame():
    browser = None

    # ----------------------------------------------------
    # 内置函数
    # ----------------------------------------------------
    def __init__(self):
        '''
        构造函数，初始化日志文件
        '''
        self.cfg = my_cfg.my_config()

        my_log.init_log()



    def quit(self):
        '''
        退出测试框架
        :return:
        '''
        if self.browser is not None:
            self.browser.quit()

    # ----------------------------------------------------
    # 异常处理
    # ----------------------------------------------------
    def proc_except(self, e):
        '''
        异常处理
        将触发异常的文件，代码行，异常消息写入日志
        :param e:
        :return:
        '''
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_log.log("异常：{0},ln{1}: {2}".format(
            fname, exc_tb.tb_lineno, e))

    # ----------------------------------------------------
    # 在DOM子树中搜索结点
    # ----------------------------------------------------
    def get_xml_node_text(self, root, tag):
        '''
        从root子树中搜索tag
        成功返回tag的文本（转换为小写字符）；失败则抛出异常
        :param root:
        :param tag:
        :return:
        '''
        if root == None:
            raise EXCP.my_exception("异常：输入项为空")
        node = root.find(tag)
        if node is None:
            raise EXCP.my_exception('异常：不能找到"{0}"标签'.format(tag))
        else:
            return node.text

    # ----------------------------------------------------
    # 定位页面元素
    # ----------------------------------------------------
    def selenium_get_elem_by_xpath(self, xpath):
        '''
        按照xpath搜索页面元素
        :param xpath:
        :return: 成功返回元素，否则抛出异常
        '''
        elem = None
        try:
            elem = self.browser.find_element_by_xpath(xpath)
            ret = elem
        except NoSuchElementException as e:
            raise EXCP.my_exception('异常：未找到xpath"{0}"'.format(xpath))
        finally:
            return elem

    def selenium_input_by_xpath(self, xpath, args):
        '''
        按照xpath搜索页面元素，
        若发现元素，则向其输入args；否则抛出异常。
        :param xpath:
        :param args:
        :return:
        '''
        elem = self.selenium_get_elem_by_xpath(xpath)
        elem.send_keys(args)

    def selenium_check_text_by_xpath(self, xpath, args):
        '''
        按照xpath搜索页面元素，
        若元素文本与args相同，返回True；否则抛出异常。
        :param xpath:
        :param args:
        :return:
        '''
        ret = False
        elem = self.selenium_get_elem_by_xpath(xpath)
        if elem.text == args:
            ret = True
        else:
            raise EXCP.my_exception('异常：{0}，未找到期望的文本"{1}"'.format(
                elem.text, args))
        return ret

    # ----------------------------------------------------
    # 校验码识别
    # ----------------------------------------------------
    def jym_proc_4(self, image_element, file_name):
        '''
        校验码处理，方法四
        使用pyAutoGUI完成界面操作
        :param browser:
        :param image_element:
        :param file_name:
        :return:
        '''
        # 鼠标移到屏幕中央
        screenWidth, screenHeight = pyautogui.size()
        pyautogui.moveTo(screenWidth / 2, screenHeight / 2)

        root_path = os.path.dirname(file_name)

        # 右键弹出菜单
        ActionChains(self.browser).context_click(image_element).perform()
        pyautogui.press("down")
        pyautogui.press("down")
        pyautogui.press("enter")

        time.sleep(1)

        screenWidth, screenHeight = pyautogui.size()
        pyautogui.moveTo(screenWidth / 4, screenHeight / 4)

        time.sleep(1)

        # 弹出“另存为”对话框
        print(file_name)
        pyautogui.typewrite(file_name)
        pyautogui.press("enter")
        pyautogui.press("tab")
        pyautogui.press("enter")



    # ----------------------------------------------------
    # 处理xml中的测试步骤
    # ----------------------------------------------------
    def tpl_openurl(self, node):
        '''
        处理tpl_openurl模板
        在node子树中搜索<url>标签，并在浏览器中打开<url>url</url>
        成功返回True，否则返回失败并抛出异常
        :param node:
        :return:
        '''
        ret = False
        try:
            url = self.get_xml_node_text(node, "url")
            func = self.get_xml_node_text(node, "Func")

            my_log.log("（tpl_openurl）{0}:{1}".format(
                func, url))

            self.browser.get(url)
            ret = True
        except EXCP.my_exception as e:
            self.proc_except(e)
        finally:
            return ret


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
            func = self.get_xml_node_text(node, "Func")

            my_log.log("（tpl_input）{0}:{1},{2},{3}".format(
                func, by, bywhere, args))

            if by == "xpath":
                self.selenium_input_by_xpath(bywhere, args)
        except EXCP.my_exception as e:
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
            func = self.get_xml_node_text(node, "Func")

            my_log.log("（tpl_submit）{0}:{1},{2}".format(
                func, by, bywhere))

            if by == "xpath":
                self.selenium_input_by_xpath(bywhere, Keys.ENTER)
        except EXCP.my_exception as e:
            self.proc_except(e)

    def tpl_recg_code(self, node):
        '''
        获取校验码
        :param node: <step></step>结点
        :return: 成功输入校验码，返回True，否则返回False
        '''
        ret = False
        tmp_file = self.cfg.root_path + '\\' + self.cfg.tmp_image_file
        img_file = self.cfg.root_path + '\\' + self.cfg.jym_image_file
        try:
            image_By = self.get_xml_node_text(node, "image_By")
            image_ByWhere = self.get_xml_node_text(node, "image_ByWhere")
            input_By = self.get_xml_node_text(node, "input_By")
            input_ByWhere = self.get_xml_node_text(node, "input_ByWhere")
            submit_By = self.get_xml_node_text(node, "submit_By")
            submit_ByWhere = self.get_xml_node_text(node, "submit_ByWhere")
            func = self.get_xml_node_text(node, "Func")

            if image_By == "xpath":
                Image_elem = self.selenium_get_elem_by_xpath(image_ByWhere)

            if input_By == "xpath":
                input_elem = self.selenium_get_elem_by_xpath(input_ByWhere)

            if submit_By == "xpath":
                submit_elem = self.selenium_get_elem_by_xpath(submit_ByWhere)

            # 下载校验码图片文件
            self.jym_proc_4(Image_elem, tmp_file)

            # time.sleep(20)
            jym = "ok"

            # 输入校验码
            self.selenium_input_by_xpath(input_ByWhere, jym)

            # 提交
            self.selenium_input_by_xpath(submit_ByWhere, Keys.ENTER)

            my_log.log("（tpl_recg_code）{0}:{1},{2}".format(
                func, image_By, image_ByWhere))

            ret = True

        except EXCP.my_exception as e:
            self.proc_except(e)
        finally:
            return ret


    def tpl_check(self, node):
        '''
        处理tpl_check模板
        按照<ByWhere>指定的xpath定位到文本，
        与<Args>指定的参数相同，则成功。
        :param node: <step></step>结点
        :return: 成功返回True
        '''
        ret = False
        try:
            by = self.get_xml_node_text(node, "By")
            bywhere = self.get_xml_node_text(node, "ByWhere")
            action = self.get_xml_node_text(node, "Action")
            args = self.get_xml_node_text(node, "Args")
            success_info = self.get_xml_node_text(node, "success_info")
            fail_info = self.get_xml_node_text(node, "fail_info")
            func = self.get_xml_node_text(node, "Func")

            my_log.log("（tpl_check）{0}:{1},{2},{3}".format(
                func, by, bywhere, args))

            if by == "xpath":
                ret = self.selenium_check_text_by_xpath(bywhere, args)
            if ret == True:
                my_log.log(success_info)
            else:
                my_log.log(fail_info)
        except EXCP.my_exception as e:
            self.proc_except(e)
        finally:
            return ret

    #----------------------------------------------------------
    def get_head(self, root):
        '''
        处理xml中与测试步骤无关的部分
        成功返回True，否则返回False，并抛出异常。
        :param root:
        :return:
        '''
        ret = False
        try:
            # 浏览器类型
            browser_type = self.get_xml_node_text(root, "Browser")
            if browser_type.lower() == "chrome":
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

            ret = True
        except EXCP.my_exception as e:
            self.proc_except(e)
        finally:
            return ret


    def get_steps(self, step):
        '''
        执行测试步骤
        :param step:
        :return:
        '''
        ret = False
        try:
            for node in step:
                id = self.get_xml_node_text(node, "TemplateId")

                # 处理tpl_openurl模板
                if id == "tpl_openurl":
                    self.tpl_openurl(node)
                    continue

                # 处理tpl_input模板
                if id == "tpl_input":
                    self.tpl_input(node)
                    continue

                # 处理tpl_submit模板
                if id == "tpl_submit":
                    self.tpl_submit(node)
                    continue

                # 处理tpl_check模板
                # todo: firefox，单步成功，运行失败。问题待查。
                if id == "tpl_check":
                    ret = self.tpl_check(node)
                    continue

                # 获取校验码
                if id == "tpl_recg_code":
                    ret = self.tpl_recg_code(node)
                    continue


        except EXCP.my_exception as e:
            self.proc_except(e)

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
            my_log.log("{0}: {1}".format(
                os.path.basename(sys.argv[0]), e))
        except Exception as e:
            self.proc_except(e)
        finally:
            return ret




if __name__ == "__main__":
    try:

        fr = my_frame()

        ret = fr.exec_tc(r"./test_case/login.xml")

        fr.quit()

        my_log.log(ret)

    except Exception as e:
        print(e)

