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

    def __search_onepage(self):
        """爬取当前页面文章的的信息"""
        results = []

        if not self.check_element_exist(check_type='ID', value='gs_res_ccl_mid'):
            print('>> 当前页面不存在文章列表')
            return []
        gs_scl_top = self.driver.find_element(by=By.ID, value='gs_res_ccl_top').find_elements(by=By.CLASS_NAME, value='gs_r')
        for item in gs_scl_top:
            if '均不相符' in item.text.strip().replace('\n', ''):
                return []
        gs_scl = self.driver.find_element(by=By.ID, value='gs_res_ccl_mid').find_elements(by=By.CLASS_NAME, value='gs_scl')
        for i, item in tqdm(enumerate(gs_scl)):
            gs_fl = item.find_element(by=By.CLASS_NAME, value='gs_flb')
            gs_rt = item.find_element(by=By.CLASS_NAME, value='gs_rt')
            gs_a = item.find_element(by=By.CLASS_NAME, value='gs_a')
            gs_rt_a = gs_rt.find_element(by=By.TAG_NAME, value='a') if self.check_element_exist(check_type='TAG_NAME', value='a', source=gs_rt.get_attribute('innerHTML')) else None
            publisher_info = gs_a.text.strip().replace('\n', '')
            # 论文标题
            title = gs_rt.text.strip().replace('\n', '').split(']')[-1].strip()
            # 论文链接
            href = gs_rt_a.get_attribute('href') if gs_rt_a else ''
            # 发表年份
            #year = re.findall(r'\d{4}', publisher_info)
            firstauthor=publisher_info.split(',')[0].strip()
            lastauthor=publisher_info.split('-')[0].strip().split(',')[-1].strip()
            #year = year[-1] if year else str(-1)
            try:
                cited=gs_fl.text.strip().replace('\n', '').split('被引用次数：')[1].split('相关文章')[0].strip()
            except:
                cited='0'
            # print(f'[{i}] {title} => {href} => {publisher_info} => {year}')
            results.append({'title': title, 'href':href, 'year': self.year,'cited':int(cited.split()[0]),'source':self.source,'firstauthor':firstauthor,'lastauthor':lastauthor})
        return results

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
        
    def search(self, source,keywords, sort_bydate=False, as_ylo='', as_yhi='', max_pages=100, delay=0):
        self.source=source
        keywords = keywords.replace(' ', '+')
        sort_bydate = 'scisbd=1' if sort_bydate else ''
        url = f'https://scholar.google.com/scholar?{sort_bydate}&hl=zh-CN&as_sdt=0%2C5&q={keywords}&btnG=&as_ylo={as_ylo}&as_yhi={as_yhi}'
        # 打开Google Scholar网站
        self.driver.get(url)
        self.year=int(as_ylo)
        total_num = self.driver.find_element(by=By.ID, value='gs_ab_md').find_element(by=By.CLASS_NAME, value='gs_ab_mdw').text.strip()  # .replace('\n', '').split(',')[:-1]
        print(total_num)
        count=0
        for _ in tqdm(range(1, max_pages+1), desc='搜索中'):
            while self.check_captcha():
                pyautogui.alert(title='状态异常', text='请手动完成人机验证后，点击“已完成”', button='已完成')
                self.driver.refresh()
                time.sleep(2)
            if self.check_error() != Errors.SUCCESS:
                if pyautogui.confirm(text='请检查页面出现了什么问题;\n解决后，点击“确定”将会重试;\n否则，点击“取消”提前结束脚本;', title='状态异常', buttons=['确定', '取消']) == '取消':
                    print('>> 提前结束')
                    break
                time.sleep(2)
            onepage = self.__search_onepage()
            if not onepage:
                print('>> 当前页为空, 退出')
                self.driver.refresh()
                time.sleep(2)
                count+=1
                if count>=2:break
                else:continue
            self.results.extend(onepage)
            self.allresults.extend(onepage)
            if not self.check_element_exist(check_type='CLASS_NAME', value='gs_ico_nav_next'):
                print('>> 全部结束')
                break
            self.__scroll2bottom()
            time.sleep(0.1)
            self.driver.find_element(by=By.CLASS_NAME, value="gs_ico_nav_next").click()
            time.sleep(delay)
        

        open(os.path.join(self.out_filepath, 'total_num.txt'), 'w+').write(''.join(total_num))


    def close_browser(self):
        # 关闭浏览器
        self.driver.quit()

    
    def save_file(self, filename='scholar.xlsx', nodup=False):
        unique_data = self.results
        if nodup:
            # 根据href字段进行去重
            unique_data = [dict(t) for t in {tuple(d.items()) for d in unique_data}]
        print(f'>> 去重效果：{len(self.results)} => {len(unique_data)}')
        print(os.path.join(self.out_filepath, filename))
        #pyperclip.copy(str(unique_data))
        unique_data = pd.DataFrame(unique_data).sort_values(by='cited',ascending=False).dropna().reset_index(drop=True)
        unique_data.dropna().reset_index(drop=True).to_excel(os.path.join(self.out_filepath, filename), index=False)#, encoding='utf-8'
    def statistical_information(self):
        pass


class AnalyzeDraw:
    def __init__(self, out_filepath, filename='scholar.xlsx') -> None:
        self.out_filepath = out_filepath
        if not os.path.exists(self.out_filepath):
            os.mkdir(self.out_filepath)
        self.filename = filename
        self.df = pd.read_excel(os.path.join(self.out_filepath, filename))
    
    def draw_wordcloud(self):
        """提取title生成词云"""
        # 定义停用词集合
        english_stopwords = set(stopwords.words('english'))
        # 清洗和转换标题列
        self.df['title'] = self.df['title'].astype(str)
        # 提取英文标题并排除非英文内容
        english_titles = self.df['title'].apply(lambda x: ' '.join([word.lower() for word in nltk.word_tokenize(x) if word.isalpha() and word.lower() not in english_stopwords]))
        # 将所有英文标题合并为一个字符串
        text = ' '.join(english_titles)
        # 创建词云对象
        wc = WordCloud(width=800, height=400, background_color='white').generate(text)
        wc.to_file(os.path.join(self.out_filepath, f'{self.filename}.jpg'))

    def draw_wordsfrequency(self):
        # 停用词列表
        stop_words = ['a', 'an', 'and', 'or', 'in', 'on', 'for', 'with', 'the', 'using', 'based', 
                      'to', 'by', 'its', 'it', '&', 'as', 'via', 'base', 'improve', 'improved',]
        # 分词并计算词频
        word_counts = Counter(' '.join(self.df['title']).lower().split())
        # 去除停用词
        for stop_word in stop_words:
            word_counts.pop(stop_word, None)
        # 按照词频从高到低排序
        sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        # 提取词和频率
        words = [item[0] for item in sorted_counts]
        freqs = [item[1] for item in sorted_counts]

        # 创建DataFrame保存词频数据
        df_freq = pd.DataFrame({'Word': words, 'Frequency': freqs})
        # 保存词频数据到Excel文件
        df_freq.to_excel(os.path.join(self.out_filepath, 'word_frequency.xlsx'), index=False)
        

if __name__ == '__main__':
    initkeywords = input('>> 请输入搜索关键词: ').strip()
    if (input('>> 是否只在标题中搜索关键词y/n： ').strip() or 'n')=='y':
        initkeywords='allintitle: '+initkeywords
    as_ylo = input('>> 请输入开始年份(留空为2017pytorch): ').strip() or '2017'
    as_yhi = f'{datetime.datetime.today().year}'# or input('>> 请输入结束年份(留空为不限): ').strip()
    max_pages = '100'# or input('>> 请输入爬取多少页(最多为100): ').strip()
    sort_bydate = False
    root = '_'.join(initkeywords.replace('"', '').replace(':', '').split())
    if not os.path.exists(root):
        os.mkdir(root)
    anssource = input('>>给出source(all/cv/trans/arxiv/ai):').strip()
    if anssource=='cv' or anssource=='':
        l=['CVPR', 'ICCV', 'ECCV', 'TPAMI', 'TIP']
    elif anssource=='ai':
        l=['CVPR', 'ICCV', 'ECCV', 'TPAMI','TIP','NIPS','AAAI','IJCAI','MM','ICML','arxiv']
    elif anssource=='all':
        l=['ALL']
    else:
        l=anssource.split(',')
    print(l)
    scholar = Scholar()
    scholar.start_browser(wait_time=60)
    for source in l:
        if source=='CVPR':
            keywords=initkeywords+' source:Proceedings source:of source:the source:IEEE/CVF source:Conference source:on source:Computer source:Vision source:and source:Pattern source:Recognition'
        elif source=='ICCV':
            keywords=initkeywords+' source:Proceedings source:of source:the source:IEEE/CVF source:International source:Conference source:on source:Computer source:Vision'
        elif source=='ECCV':
            keywords=initkeywords+' source:European source:Conference source:on source:Computer source:Vision'
        elif source=='TPAMI':
            keywords=initkeywords+' source:IEEE source:Transactions source:on source:pattern source:analysis source:and source:Machine source:Intelligence'
        elif source=='TIP':
            keywords=initkeywords+' source:IEEE source:Transactions source:on source:Image source:Processing'
        elif source=='ALL':
            keywords=initkeywords
        elif source=='trans':
            keywords=initkeywords+' source:transactions'
        elif source=='IJCAI':
            keywords=initkeywords+' source:International source:Joint source:Conference source:on source:Artificial source:Intelligence'
        elif source=='AAAI':
            keywords=initkeywords+' source:Proceedings source:of source:the source:AAAI source:Conference source:on source:Artificial source:Intelligence'
        elif source=='ICML':
            keywords=initkeywords+' source:International source:Conference source:on source:Machine source:Learning'
        elif source=='arxiv':#ICLR
            keywords=initkeywords+' source:arXiv source:preprint'
        elif source=='NIPS':
            keywords=initkeywords+' source:Advances source:in source:neural source:information source:processing source:systems'
        elif source=='MM':
            keywords=initkeywords+' source:ACM source:international source:conference source:on source:Multimedia'
        else:
            keywords=initkeywords+' source:'+source

        out_filepath=os.path.join(root,f'{source}_{as_ylo}_{as_yhi}')
        scholar.get_path(out_filepath)

        for i in range(int(as_ylo),int(as_yhi)+1):
            scholar.search(source,keywords, sort_bydate, str(i), str(i), max_pages=int(max_pages), delay=random.randint(0, 0))
        if len(scholar.results):
            scholar.save_file(nodup=True)
        #analyze = AnalyzeDraw(out_filepath)
        #analyze.draw_wordcloud()
        #analyze.draw_wordsfrequency()
        print('>> done <<')
    scholar.close_browser()
    unique_data = pd.DataFrame(scholar.allresults).sort_values(by='cited', ascending=False).dropna().reset_index(drop=True)
    unique_data.drop_duplicates(subset=['title'])
    unique_data.dropna().reset_index(drop=True).to_excel(os.path.join(root, 'scholar.xlsx'),
                                                         index=False)  # , encoding='utf-8'
    # 使用 os.path.join 构建文件路径
    file_path = os.path.join(root, 'scholar.xlsx')

    # 使用 Pandas 读取 Excel 文件
    df = pd.read_excel(file_path)

    # 按 'cited' 列进行倒序排序
    df_sorted = df.sort_values(by='cited', ascending=False)

    # 将排序后的数据保存回原文件
    df_sorted.to_excel(file_path, index=False)

    print('>> all done <<')
