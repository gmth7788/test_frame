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
import json

import pytesseract
from PIL import Image

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

    def fix_img(self, input_file, output_file):
        '''
        修理校验码图片
        1）将灰色线条改为白色；
        2）黑色线框改为白色；
        3）蓝色字体改为黑色；
        :param input_file: 校验码文件名
        :return:
        '''
        img = Image.open(input_file)  # 读取系统的内照片
        width = img.size[0]  # 长度
        height = img.size[1]  # 宽度
        for i in range(0, width):  # 遍历所有长度的点
            for j in range(0, height):  # 遍历所有宽度的点
                data = (img.getpixel((i, j)))  # 打印该图片的所有点
                if not ((data[0] == 0) and (data[1] == 0) and (data[2] == 255)):
                    img.putpixel((i, j), (255, 255, 255))
                else:
                    img.putpixel((i, j), (0, 0, 0))
        img = img.convert("RGB")  # 把图片强制转成RGB
        img.save(output_file)  # 保存修改像素点后的图片

    def recg_jym(self, input_file):
        '''
        返回校验码
        :param input_file: 经过修整的校验码图片
        :return: 成功返回校验码，否则抛出异常
        '''
        img = Image.open(input_file)
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        text = text.replace(' ','')
        my_log.log("获得识别码:{0}".format(text))
        if len(text) != 4:
            raise EXCP.my_exception('异常：校验码识别失败"{0}"'.format(text))
        return text


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

            my_log.log('''（tpl_openurl）{0}
            Url:{1}'''.format(
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

            my_log.log('''（tpl_input）{0}:
            By:{1}
            ByWhere:{2}
            Args:{3}'''.format(
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

            my_log.log('''（tpl_submit）{0}:
            By:{1}
            ByWhere:{2}'''.format(
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
        for i in range(3):
            try:
                image_By = self.get_xml_node_text(node, "image_By")
                image_ByWhere = self.get_xml_node_text(node, "image_ByWhere")
                input_By = self.get_xml_node_text(node, "input_By")
                input_ByWhere = self.get_xml_node_text(node, "input_ByWhere")
                submit_By = self.get_xml_node_text(node, "submit_By")
                submit_ByWhere = self.get_xml_node_text(node, "submit_ByWhere")
                codeChange_By = self.get_xml_node_text(node, "codeChange_By")
                codeChange_ByWhere = self.get_xml_node_text(node, "codeChange_ByWhere")
                func = self.get_xml_node_text(node, "Func")

                if image_By == "xpath":
                    Image_elem = self.selenium_get_elem_by_xpath(image_ByWhere)

                if input_By == "xpath":
                    input_elem = self.selenium_get_elem_by_xpath(input_ByWhere)

                if submit_By == "xpath":
                    submit_elem = self.selenium_get_elem_by_xpath(submit_ByWhere)

                if codeChange_By == "xpath":
                    codeChange_elem = self.selenium_get_elem_by_xpath(codeChange_ByWhere)

                # 下载校验码图片文件
                self.jym_proc_4(Image_elem, tmp_file)
                time.sleep(1)

                # 修饰图片
                self.fix_img(self.cfg.tmp_image_file, self.cfg.tmp1_image_file)

                # 识别校验码
                jym = self.recg_jym(self.cfg.tmp1_image_file)

                # 输入校验码
                self.selenium_input_by_xpath(input_ByWhere, jym)
                time.sleep(1)

                # 提交
                self.selenium_input_by_xpath(submit_ByWhere, Keys.ENTER)

                my_log.log("（tpl_recg_code）{0}:{1},{2}".format(
                    func, image_By, image_ByWhere))

                time.sleep(1)


                # todo: 捕获对话框
                try:
                    # 校验码不正确对话框
                    alert = self.browser.switch_to.alert()
                    # print(alert.text)
                    # self.browser.switch_to_alert().accept()
                    # 点击刷新校验码
                    codeChange_elem.click()
                    time.sleep(1)
                    continue
                except NoAlertPresentException as msg:
                    # 校验码通过校验，退出循环
                    ret = True

            except EXCP.my_exception as e:
                self.proc_except(e)
            finally:
                if True != ret:
                    codeChange_elem.click()
                    time.sleep(1)
                else:
                    break

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

            my_log.log('''（tpl_check）{0}:
            By:{1}
            ByWhere:{2}
            Args:{3}'''.format(
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

    def get_token(self, url, type, header, data, token_name):
        '''
        获得访问令牌token
        :param url: 访问地址
        :param type: 请求类型
        :param header: 请求头
        :param data: 请求数据
        :param token_name: 令牌名称
        :return:
        '''
        token = None
        if type.lower() == 'post':
            r = requests.post(url, json=data, headers=header)
            token = r.json()[token_name]
        return token

    def tpl_itf(self, node):
        '''
        处理tpl_itf模板
        https://www.cnblogs.com/leiziv5/p/6422954.html
        :param node: <step></step>结点
        :return: 成功返回True
        '''
        try:
            url = self.get_xml_node_text(node, "Url")
            type = self.get_xml_node_text(node, "Type")
            header = self.get_xml_node_text(node, "Head")
            data = self.get_xml_node_text(node, "Data")
            func = self.get_xml_node_text(node, "Func")
            token_name = self.get_xml_node_text(node, "token_name")

            header = json.loads(header)
            data = json.loads(data)

            # 记录日志
            my_log.log('''（tpl_itf）{0}:
            Url:{1}
            Type:{2}
            Header:{3}
            Data:{4}'''.format(
                func, url, type, header, data))

            if token_name is not None:
                # 如果此项为空，则获取令牌
                token = self.get_token(url, type, header,
                                       data, token_name)
                header[token_name] = token
                # 保存到配置文件中
                self.cfg.set_config('tokens', 'sso_token', token)
            else:
                # 从配置文件获取令牌
                self.cfg.get_config()

                header['sso_token'] = self.cfg.sso_token

                if type.lower() == 'get':
                    # todo: 待确认
                    r = requests.get(url, headers=header, params=data)
                    print("url:{0}".format(r.url))
                    print("head:{0}".format(r.headers))
                    print("text:{0}".format(r.text))
                else:
                    r = requests.post(url, json=data, headers=header)
                    print("url:{0}".format(r.url))
                    print("head:{0}".format(r.headers))
                    print("text:{0}".format(r.text))

        except EXCP.my_exception as e:
            self.proc_except(e)







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

                # 处理tpl_recg_code模板
                if id == "tpl_recg_code":
                    ret = self.tpl_recg_code(node)
                    continue

                # 处理tpl_itf模板
                if id == "tpl_itf":
                    ret = self.tpl_itf(node)
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
            ret = True
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

        # ret = fr.exec_tc(r"./test_case/login.xml")
        ret = fr.exec_tc(r"./test_case/qryOrgByID.xml")

        fr.quit()

        my_log.log(ret)

    except Exception as e:
        print(e)

