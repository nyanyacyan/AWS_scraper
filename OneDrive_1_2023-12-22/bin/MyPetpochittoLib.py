# coding: utf-8

# -----------------------------------
# PETポチっとスクレイピングライブラリ
# 　制作2023.12.6
# -----------------------------------

from time import sleep #sleep用
from bin import MyFileIOLib #GUIアプリ起動用ライブラリ
from bin import MyReg #正規表現ライブラリ
import random #乱数使用。メルカリにアクセスする場合にランダムに時間を空ける
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import os


# xpath一覧

#mercari_login_from_mail_xpath = "//mer-button[@location-2='email_button']/a"  # メールでログイン



class MyPetpochittoLib():
    browser = None#ブラウザーの表示・操作用
    wait = None#メルカリにアクセスする前に前回のアクセスからのインターバルを設定する
    DEBUGMODE = False

    # initialize-
    def __init__(self, browser, DEBUGMODE=False, **kwargs):
        self.browser = browser
        self.DEBUGMODE = DEBUGMODE
        # if not self.loginCheck(120):  # メルカリにログインしていない場合はログイン画面を表示。最大120秒待機しログインできなければエラー終了
        #     raise Exception("メルカリのログインに失敗しました。")
        # print("メルカリにログイン中です")
        #
        # sleep(3)  #連続アクセス防止
        #self.browser.set_URL("https://jp.mercari.com/mypage/listings")
        #sleep(2)  # 起動まで少し待つ

    # destructor
    def __del__(self):
        if self.DEBUGMODE: print("MyNetseaLib __del__:")
        pass

    #ログイン中かチェック。ログイン出来たらTrueを返す。出来なかったらFalseを返す.waitに指定がある場合はwait秒ログインチェックを繰り返す
    def loginCheck(self, wait = 60):
        self.browser.set_URL("https://www.petpochitto.com/")
        sleep(1)#リダイレクトを待つ

        print_flug = True

        for count in range(wait):
            ##ログアウトが無ければログイン出来ていない
            elements = self.browser.find_elementsByXpath("//li[@class='__mypage']")
            if len(elements) < 1:
                if print_flug:
                    print("\033[34m■■■■■■PETポチッとへ未ログインです。ログインをしてください■■■■■■\033[0m")
                    print_flug = False
                    self.browser.set_URL("https://www.petpochitto.com/login.php")
                else:
                    print(".",end="")

            else:
                print("\033[32mPETポチッとへログイン済みです\033[0m")
                break


            sleep(5)

        #指定秒経過しても未ログインの場合Falseを返す
        return False

    # 商品価格の取得 引数：jancode※コードのエラーチェック無, 戻り値price[価格,"url"] 取得に失敗["",""]
    def getPriceByJancode(self, jancode):
        #print(f"{jancode}でPETポチッとを検索します。")

        # ①jancodeから価格(最安値,リンク)を取得※期間限定2重価格の場合は元の価格
        price = [999999999, ""]

        # JANコードで検索
        self.browser.set_URL("https://www.petpochitto.com/list.php?keyword=" + jancode)
        # 「お探しの検索条件に合致する商品は見つかりませんでした。」と表示された場合一致無
        elements = self.browser.find_elementsByXpath("//p[text()= 'お探しの検索条件に合致する商品は見つかりませんでした。']")
        if len(elements) > 0:
            return ["条件に一致する商品は見つかりませんでした。", ""]

        # 入れ物を取得
        elements = self.browser.find_elementsByXpath("//ul[@class= '__product']")
        elements = elements[0].find_elements(By.TAG_NAME, "li")

        print("PETポチッと", end="")
        print(len(elements),end="")
        print("件ヒットしました。")

        # もし検索結果が0件だったら条件に一致するものなし
        if len(elements) < 1:
            return ["条件に一致する商品は見つかりませんでした。", ""]

        # 検索結果すべてに対して走査
        for element in elements:
            # 価格の取得
            price_elements = element.find_elements(By.CLASS_NAME, "__unit-price")
            if len(price_elements) > 0:

                if self.DEBUGMODE:
                    print("商品の価格:", end="")
                    print(price_elements[0].text)

                price_buf = MyReg.rtnNumFromStr(price_elements[0].text)

                # もし価格があり、価格が登録価格より安い場合登録
                if price_buf != "":
                    if price_buf < price[0]:
                        # URLの取得
                        # url_elements = self.browser.find_elementsByXpath("//a", element)
                        url_elements = element.find_elements(By.TAG_NAME, "a")
                        if (len(url_elements) < 1):
                            if self.DEBUGMODE:
                                print(f"{jancode}:{price_buf}のURLが見つかりません。スキップします。")
                        else:
                            url = url_elements[0].get_attribute('href')
                            if self.DEBUGMODE:
                                print(f"見つかった商品：[{price_buf},{url}]　現在の登録：[{price[0]},{price[1]}]")
                            price[0] = price_buf
                            price[1] = url
                        print(price)

        # もし価格が999999999と変わらなければ取得失敗
        if price[0] == 999999999:
            price[0] = "価格が取得できませんでした。"

        return price


# ----------------------------
# メインここから
# ----------------------------
if __name__ == '__main__':

    print(f"MyNetseaLib main")

