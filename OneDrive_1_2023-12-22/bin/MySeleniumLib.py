# coding: utf-8

# -----------------------------------
# Seleniumを用いたスクレピングスクリプト
# Seleniumバージョン4.1.0
# 　制作2022.10.29
# -----------------------------------

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
import os #getcwd()用
from time import sleep

DEBUGMODE = False

class MySeleniumLib():
    browser = None  # chromeドライバ用変数


    #initialize-ブラウザの起動
    def __init__(self, profilePath="/bin/profile",*args):
        #OSの判定。
        #Windowなら
        if os.name == 'nt':
            binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # 通常版を使用
            #binary_location = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"  # ベータ版を使用
            executable_path = "./bin/chromedriver_win32/chromedriver.exe"
        #Mac or Linuxなら
        elif os.name == 'posix':
            print("selenium:posix")
            # binary_location = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"  # ベータ版を使用
            binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # ベータ版を使用
            executable_path = "./bin/chromedriver_win32/chromedriver.exe"


        options = webdriver.ChromeOptions()
        options.add_argument('--user-data-dir=' + os.getcwd() + profilePath)
        options.binary_location =binary_location
        # ヘッドレスモードでブラウザを起動
        #options.add_argument('--headless')
        # ユーザー情報を偽装：参考　https://engineerismydream33.org/?p=152
        # UA = 'Mozilla/5.0 (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        # options.add_argument('--user-agent=' + UA)
        #webdriverを偽装する1。参考：https://www.youtube.com/watch?v=vZetEabHGmw
        options.add_argument('--disable-blink-features=AutomationControlled')

        try:
            chrome_service = service.Service(executable_path=executable_path)
            #self.browser = webdriver.Chrome(service=chrome_service, options=options)
            self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            self.browser.implicitly_wait(2) #要素が見つかるまで最大指定秒待機します。要素が見つかればそれ以上待機しません。
            # webdriverを偽装する2。参考：https://www.youtube.com/watch?v=vZetEabHGmw
            self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        except Exception as e:
             #起動に失敗した場合はエラーをライズ
             print(e)
             raise ValueError("ブラウザの起動に失敗しました。")

    #destructor.プログラム終了時にdel MySeleniumLib を推奨
    def __del__(self):
        if DEBUGMODE:print("MySeleniumLib __del__:quit browser")
        self.quit_browser()

    def getBrowser(self):
        return self.browser

    def quit_browser(self):
        if self.browser is not None:
            self.browser.quit()  # closeはブラウザを閉じるコマンド,quit()の方がよさそう
            sleep(5)
            self.browser = None

    #URLを表示する
    def set_URL(self, url):
        try:
            self.browser.get(url)
        except Exception as e:
            print("ページの表示が出来ませんでした。")
        #sleep(10)

    def get_URL(self):
        return self.browser.current_url

    def find_elementsByXpath(self, xpath, element=None):
        if(element is None):
            #print("element is None")
            return self.browser.find_elements(By.XPATH, xpath)
        else:
            #print("element is Not None")
            return element.find_elements(By.XPATH, xpath)

    def current_url(self):
        return self.browser.current_url

    #ページソースの取得
    def get_page_source(self):
        return self.browser.page_source

    #windowサイズの設定
    def set_window_size(self, x,y):
        self.browser.set_window_size(x,y)


    #ウィンドウのスクロールyピクセルscrollする
    def window_scroll(self,y):
        self.browser.execute_script("window.scrollBy(0, "+str(y)+");")

    #javascriptの実行
    def execute_script(self,script):
        self.browser.execute_script(script)