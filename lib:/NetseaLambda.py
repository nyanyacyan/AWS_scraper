# coding: utf-8

# ----------------------------------------------------------------------------------
# ローカル　スクレイピング実行ファイル
# 　制作2023.12.31
#  使用ライブラリ
#selenium==4.1.0
#webdriver_manager==3.8.6
#gspread==5.9.0
#gspread-formatting==1.1.2
#oauth2client==4.1.3


#   流れ
# 関数定義 → 自身の作成したファイルのを転記して修正
# logger定義 → 自身の作成したファイルのを転記して修正
# URL指定 → 自身の作成したファイルのを転記して修正
# Seleniumのoption定義 → 自身の作成したファイルのを転記して修正
# ブラウザを開く→ 作成元からの転記
# ログインする→ 新規作成（ログインボタンの有無で判断→ログイン処理）
# リクエストBODYの取得→JAN→ 新規作成
# 検索ボックスを取得して入力→ 作成元からの転記
# レスポンスを返す→価格 + URL→ 新規作成

# lambda関数を作成→ Lambda Layersを使用して構築→ テスト



# リクエスト元のデータ == JAN
# レスポンスデータ == 価格 + URL
# AWSCloudShellにてdriver+seleniumをインストール


# ----------------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
import logging
import json


def NetseaLambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(f"処理スタート")

    url = "https://www.netsea.jp/"

    wait = 60
    print_flug = True

    # webdriver（Chrome）のオプションを使うことを宣言
    options = webdriver.ChromeOptions()

    # webdriverのどんなオプション使うのかを選定
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1200x1000")  # サイズを大きくすることでsend_keysでの
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")

    # headlessのChromeバージョンを選定
    options.binary_location = "/opt/headless/headless-chromium"

    logger.info(f"ブラウザのパスを指定")

    browser = webdriver.Chrome(
        # Chromeを操作できるようにするためのdriverをAWSにあるパスを選定
        executable_path="/opt/headless/chromedriver",
        options=options
    )

    logger.info(f"ブラウザを開く")

    # URLを開く
    browser.get(url)


    # リクエストのBODYを取得
    request_body = event.get('local_jan_code')

    logger.info("リクエストボディが存在します: %s", request_body)
    logger.info("ページロードを待機しています...")

    # ページが完全にロードされるのを待つ
    WebDriverWait(browser, 3).until(
        lambda browser: browser.execute_script('return document.readyState') == 'complete'
    )

    logger.info("ページが完全にロードされました。")

    # 広告が出てきたらスキップ
    ad_elements = browser.find_elements_by_xpath("//i[@class='fa fa-close']")
    if len(ad_elements) > 0:
        ad_elements[0].click()
        sleep(1)  

    print_flug = True

    # 広告が出てきたらスキップ→ 転記
    # ログインができてるかを確認→ 自動ログイン
    # waitの分だけ実施するためのループ処理
    for count in range(wait):
        ##カートボタンが無ければログイン出来ていない
        try:
            elements = browser.find_elements_by_xpath("//i[@class= 'fa fa-shopping-cart']")
            if len(elements) < 1:
                if print_flug:
                    print("\033[34m■■■■■■NETSEAへ未ログインです。自動ログインをします■■■■■■\033[0m")
                    print_flug = False
                    browser.get("https://www.netsea.jp/login")

                    username_field = browser.find_element_by_id("userId")
                    password_field = browser.find_element_by_id("pass")

                    # 認証情報
                    username_field.send_keys('info@abitora.jp')
                    password_field.send_keys('Abitra2577')

                    # ログインボタンをクリック
                    login_button = browser.find_element_by_xpath("//button[@class='btnType01 btnColor04 btnEffects fSize16 fNormal btmMgnSet']")
                    login_button.click()

                else:
                    print(".",end="")  # 待機を"."で表してる。

            else:
                print("\033[32mNETSEAへログイン済みです\033[0m")
                return True  # ログイン成功

            sleep(5)
        except NoSuchElementException:
            print("ログインフォームの要素が見つかりません。")
            return{'statusCode': 500, 'body': json.dumps('ログインフォーム要素が見つかりません')}
        
        except TimeoutException:
            print("ページの読み込みがタイムアウトしました。")
            return{'statusCode': 500, 'body': json.dumps('ページの読み込みタイムアウト')}
        
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            return{'statusCode': 500, 'body': json.dumps(f'予期せぬエラー: {e}')}
            

    # #指定秒経過しても未ログインの場合Falseを返す
    # return False

    if request_body:
        # jsonファイルの読み込みを実施
        # 読み込みができなかったらログを残す。
        try:
            request_data = json.loads(request_body)  # jsonを解析

            jan = request_data.get('jan')
            product_name = request_data.get('product_name')

            logger.info(f"解析完了: JAN: {jan}, 商品名: {product_name}")

        except json.JSONDecodeError as e:
            logger.error(f"解析エラー:{e}")


        # 検索バーを探す
        # "keyword"→最初の要素→name属性の値
        # 検索バー（IDがkeyword）が見つからなかったらログを残す
        try:
            elements = browser.find_elements_by_id("search_fixed_input")
            if elements:
                element = elements[0] 
                name_attribute = element.get_attribute('name')
                logger.info(f"検索バーをサーチ済み")
                logger.info(f"Element tag name: {element.tag_name}")
                logger.info(f"Element name attribute: {name_attribute}")

            else:
                logger.info(f"検索バーが見つからない")

        except TimeoutException:
            logger.error(f"検索バー:タイムアウト。")

        # テキストボックスに検索ワードを入力
        # キーワードが入力できなかったらログを残す。
        try:
            if element.is_displayed():
                element.send_keys(jan + " " + product_name)
                logger.info("キーワード入力に成功")
            else:
                logger.info("要素が表示されていません")

        except Exception as e:
            logger.error(f"キーワード入力失敗: {e}")

        # 検索ボタンを探す
        # クリックができるようになるまで最大6秒、動的待機
        search_buttan = browser.find_elements_by_id("search_btn")

        logger.info("検索ボタンを探すことを開始")

        # 検索ボタンをクリック
        search_buttan.click()

        logger.info("検索ボタンをクリック")

        # ショーケースを見つける
        # 見つけるまで最大6秒、動的待機
        all_showcasebox = WebDriverWait(browser, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='showcaseBox']"))
        )

        #もし検索結果が0件だったら条件に一致するものなし
        if len(all_showcasebox) < 1:
            return ["条件に一致する商品は見つかりませんでした。",""]
        
        # showcaseboxの数をカウント
        count_showcasebox = len(all_showcasebox)
        logger.info(f"'showcasebox'の数: {count_showcasebox}")

        # priceを探す
        all_price = WebDriverWait(browser, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='price']"))
        )


        # 現在のページにある価格を全てリスト化する。
        all_price_list = [price.text for price in all_price]
        netsea_lambda_price = all_price_list[0]
        logger.info(f"{netsea_lambda_price}")

        # URLを見つける
        # 見つけるまで最大6秒、動的待機
        all_url = WebDriverWait(browser, 6).until(
            EC.presence_of_all_elements_located((By.XPATH, "//h3[@class='showcaseHd']/a"))
        )
        logger.info("URL取得")
        

        # 商品カタログ名
        all_url_list = [url.text for url in all_url]
        netsea_lambda_url = all_url_list[0]
        logger.info(f"{netsea_lambda_url}")

        # jsonオブジェクトの作成
        response_data = {
            "netsea_lambda_price": netsea_lambda_price,
            "lambda_url": netsea_lambda_url
        }


    else:
        logger.error("リクエストボディがありません。")

    # WebDriverを閉じる
    browser.quit()

    # jsonデータをレスポンスとして返す
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': response_data
    }