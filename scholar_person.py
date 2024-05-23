import random
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from tqdm import tqdm
import pyautogui
from bs4 import BeautifulSoup
import lxml
import pandas as pd
from enum import Enum
import pyperclip
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import os
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')


class Errors(Enum):
    SUCCESS         = '成功'
    SERVER_ERROR    = '服务器错误'


class Scholar:
    def __init__(self) -> None:
        self.driver = None
        self.results = []
        self.allresults=[]
    def get_path(self,out_filepath):
        if not os.path.exists(out_filepath):
            os.mkdir(out_filepath)

        self.results = []
        self.out_filepath=out_filepath

    def start_browser(self, wait_time=10):
        # 创建ChromeOptions对象
        options = Options()
        # 启用无头模式
        # options.add_argument("--headless")
        # 启用无痕模式
        options.add_argument("--incognito")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--no-first-run")
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument("--autoplay-policy=user-gesture-required")
        options.add_argument("--disable-features=ScriptStreaming")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-webgl")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-full-form-autofill-ios")
        options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
        options.add_argument("--disable-single-click-autofill")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-blink-features")
        # 禁用实验性QUIC协议
        options.add_experimental_option("excludeSwitches", ["enable-quic"])
        # 创建Chrome浏览器实例
        self.driver = webdriver.Chrome(options=options)
        # 等待页面加载完成
        self.driver.implicitly_wait(wait_time)

    def check_element_exist(self, value, check_type='CLASS_NAME', source=None) -> bool:
        """检查页面是否存在指定元素"""
        page_source = source if source else self.driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        if check_type == 'ID':
            return len(soup.find_all(id=value)) != 0
        elif check_type == 'CLASS_NAME':
            return len(soup.find_all(class_=value)) != 0
        elif check_type == 'TAG_NAME':
            return len(soup.find_all(value)) != 0
        elif check_type == 'FULL':
            return value in page_source
        else:
            print(f'>> 检查条件[{check_type}]不对')
        return False

    def check_captcha(self) -> bool:
        """检查是否需要人机验证；一个是谷歌学术的、一个是谷歌搜索的"""
        return self.check_element_exist(check_type='ID', value='gs_captcha_f') or \
               self.check_element_exist(check_type='ID', value='captcha-form')

    def process_error(self, error: Errors) -> bool:
        """尽可能尝试解决错误"""
        success = False
        if error == Errors.SERVER_ERROR:
            pass
        
        return success
    
    def check_error(self, try_solve = True) -> Errors:
        """检查当前页面是否出错"""
        error = Errors.SUCCESS
        if self.check_element_exist(check_type='FULL', value='服务器错误'):
            error = Errors.SERVER_ERROR
        
        # 尝试解决错误
        if try_solve and error != Errors.SUCCESS:
            error = Errors.SUCCESS if self.process_error(error) else error
        return error

    def __scroll2bottom(self):
        # 将滚动条移动到页面的底部
        self.driver.switch_to.default_content()
        js = "var q=document.documentElement.scrollTop=100000"
        self.driver.execute_script(js)
        
    def search(self, delay=0):
        url='https://scholar.google.com/citations?hl=zh-CN&user=D_S41X4AAAAJ'
        #url='https://scholar.google.com/citations?user=MOD0gv4AAAAJ&hl=en'
        #url='https://scholar.google.com/citations?user=559LF80AAAAJ&hl=zh-CN'
        #url='https://scholar.google.com/citations?user=lc45xlcAAAAJ'
        #url='https://scholar.google.com/citations?user=HsV0WbwAAAAJ&hl=en'
        #url='https://scholar.google.com.hk/citations?user=GaJXFWMAAAAJ&hl=zh-CN&oi=sra'
        #url='https://scholar.google.com.hk/citations?user=cPtzhPsAAAAJ&hl=zh-CN&oi=sra'
        #url='https://scholar.google.com/citations?user=TGXfPg4AAAAJ'
        #url='https://scholar.google.com/citations?user=Fq9SgKYAAAAJ'
        #url='https://scholar.google.com/citations?user=83WWEs4AAAAJ'
        #url='https://scholar.google.com/citations?user=7bk53mEAAAAJ'
        #url='https://scholar.google.com/citations?user=YUKPVCoAAAAJ&hl'
        #url='https://scholar.google.com/citations?hl=zh-CN&user=705qVrYAAAAJ'
        #url='https://scholar.google.com/citations?user=vEPnP6oAAAAJ'
        #url='https://scholar.google.com/citations?user=_dQWEzEAAAAJ&hl=en'
        #url='https://scholar.google.com.hk/citations?user=8Ss6ahEAAAAJ&hl=zh-CN&oi=ao'
        #url='https://scholar.google.com/citations?user=urOSnlQAAAAJ&hl=zh-CN&oi=ao'
        #url='https://scholar.google.com/citations?user=y2S02IcAAAAJ&hl=en'
        #url='https://scholar.google.com.hk/citations?user=wth-VbMAAAAJ&hl=zh-CN&oi=sra'
        #url='https://scholar.google.com.hk/citations?user=D_S41X4AAAAJ&hl=zh-CN&oi=sra'
        #url='https://scholar.google.com/citations?user=Z8PYhA4AAAAJ&hl=en&oi=ao'
        #url = 'https://scholar.google.com/citations?hl=en&user=MOD0gv4AAAAJ&view_op=list_works&sortby=pubdate'
        # 打开Google Scholar网站
        self.driver.get(url)
        name=self.driver.find_element(By.ID, 'gsc_prf_in').text.strip().replace(' ','_')
        show_more_button = self.driver.find_element(By.ID, 'gsc_bpf_more')
        while True:
            if show_more_button.get_attribute("disabled") is not None:
                result=self.driver.find_element(by=By.ID, value='gs_top').text.strip()
                break
            else:
                # Click the "Show more" button if it's not disabled
                show_more_button.click()
                time.sleep(2)
        elements_with_class_gsc_a_tr = self.driver.find_elements(By.CLASS_NAME, 'gsc_a_tr')
        # Create lists to store data for each column
        column1_data = []
        column2_data = []
        column3_data = []

        # Iterate over elements and extract data
        for element in elements_with_class_gsc_a_tr:
            # Extract data from gsc_a_t, gsc_a_c, and gsc_a_y
            gsc_a_t_text = element.find_element(By.CLASS_NAME, 'gsc_a_t').text
            gsc_a_c_text = element.find_element(By.CLASS_NAME, 'gsc_a_c').text
            gsc_a_y_text = element.find_element(By.CLASS_NAME, 'gsc_a_y').text

            # Append data to lists
            if len(gsc_a_t_text.split('\n'))==3:
                column1_data.append(gsc_a_t_text)
                column2_data.append(gsc_a_c_text)
                column3_data.append(gsc_a_y_text)

        # Create a DataFrame using the lists
        source=[i.split('\n')[2].strip().lower() for i in column1_data]
        for i in range(len(source)):
            if 'aaai' in source[i]:
                source[i]='AAAI'
            elif 'arxiv' in source[i]:
                source[i]='arXiv'
            elif 'acm international conference on multimedia' in source[i]:
                source[i]='MM'
            elif 'transactions on image processing' in source[i]:
                source[i]='TIP'
            elif 'conference on computer vision and pattern' in source[i]:
                source[i]='CVPR'
            elif 'european conference on computer vision' in source[i]:
                source[i]='ECCV'
            elif 'transactions on pattern analysis and machine intelligence' in source[i]:
                source[i]='TPAMI'
            elif 'international conference on computer vision' in source[i]:
                source[i]='ICCV'
        df = pd.DataFrame({
            'title': [i.split('\n')[0].strip().lower() for i in column1_data],
            'author':[i.split('\n')[1].strip().lower() for i in column1_data],
            'source':source,
            '1st-author':[i.split('\n')[1].strip().lower().split(',')[0].strip() for i in column1_data],
            'co-author':[i.split('\n')[1].strip().lower().split(',')[-1].strip() for i in column1_data],
            'cited': [int(i.replace('*','').strip()) if i.replace('*','').strip() else 0 for i in column2_data],
            'year': [int(i.strip()) if i.strip() else 0 for i in column3_data]
        })

        # Save DataFrame to Excel
        df.to_excel(f'{name}.xlsx', index=False)
    def close_browser(self):
        # 关闭浏览器
        self.driver.quit()


if __name__ == '__main__':
    scholar = Scholar()
    scholar.start_browser(wait_time=60)
    scholar.search(delay=random.randint(0, 0))
    scholar.close_browser()
