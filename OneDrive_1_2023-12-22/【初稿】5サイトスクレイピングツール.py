# coding: utf-8

# -----------------------------------
# 5サイトスクレイピングツール
# 　制作2023.12.04
#  使用ライブラリ
#selenium==4.1.0
#webdriver_manager==3.8.6
#gspread==5.9.0
#gspread-formatting==1.1.2
#oauth2client==4.1.3
# -----------------------------------

from bin import MySeleniumLib
from bin import MyGoogleSheetsLib
from bin import MyFileIOLib
from bin import MyNetseaLib #NETSEA用ライブラリ
from bin import MyPetpochittoLib #PETポチッと用ライブラリ
from bin import MyOroshiuriLib #卸売りドットコム
from bin import MySuperdeliveryLib #スーパーデリバリー
from bin import MyTajimayaoroshiLib #タジマヤ卸ネット

from bin import MyTimeLib
from bin import MyReg
#from bin import MyFlaskLib

from time import sleep
import random
import threading
import datetime
import traceback

DEBUGMODE = False#デバッグモードの設定。詳細な情報が標準ストリームに表示されます。


class myError():
    sheets = None

    # initialize-
    def __init__(self, sheets):
        self.sheets = sheets

    def myError(self, text, status='info'):
        print(text)
        # #現在時刻の取得
        dt_now = MyTimeLib.getDatetimeNow()

        sheets.setws("log")

        #１行追加しエラーを記録
        self.sheets.insert_row([f"{dt_now.year}/{dt_now.month}/{dt_now.day} {dt_now.hour}:{dt_now.minute}:{dt_now.second}",status, text], index=2)
        #もしエラーだったら色を変える
        if status == 'error':
            self.sheets.setColor('B2', [1, 0, 0])


# ----------------------------
# メインここから
# ----------------------------
if __name__ == '__main__':
    # ==============初期処理(プログラム開始後1度だけ実行)===========================
    # スプシの準備
    try:
        sheets = MyGoogleSheetsLib.MyGoogleSheetsLib()
    except Exception as e:
        msg = "【致命的なエラー】スプレッドシートへのアクセスに失敗しました。API設定が正しいか確認してください。error:"+str(e)
        print('\033[31m'+msg+'\033[0m')
        exit(-1);#プログラムの終了

    # エラー記載用クラスのインスタンス化
    myerror = myError(sheets)

    # ------------スプシからデータの取得(JAN,商品名)------------
    try:
        sheets.setws("【セラーID】リサーチ商品群")
    except Exception as e:
        msg = "【致命的なエラー】「【セラーID】リサーチ商品群」へのアクセスに失敗しました。シートのタブ名は変更しないでください。error:" + str(e)
        print('\033[31m' + msg + '\033[0m')
        myerror.myError(msg, status='error')
        exit(-1);  # プログラムの終了

    # 最終行を取得
    last_row = sheets.get_last_row(6)
    if DEBUGMODE:
        print("last_row="+str(last_row))

    if(last_row < 2):
        msg = "【致命的なエラー】JANコード一覧の取得に失敗しました。F列のJANの一覧が正しく記載されているかご確認ください"
        print('\033[31m' + msg + '\033[0m')
        myerror.myError(msg, status='error')
        exit(-1);  # プログラムの終了

    jancode_list = sheets.getValues("F2:Y"+str(last_row))#20列文取得するが、データがある部分だけ列になる。

    if DEBUGMODE:
        print("JANコードリスト=")
        print(jancode_list)


    # ブラウザのインスタンス化
    try:
        browser = MySeleniumLib.MySeleniumLib()  # ブラウザの実行
    except Exception as e:
        msg = "【致命的なエラー】ブラウザの起動に失敗しました。Chromeを終了し、再度実行してください。error:" + str(e)
        print('\033[31m' + msg + '\033[0m')
        if DEBUGMODE:#tracebackの表示
            print(traceback.format_exc())
        myerror.myError(msg, status='error')
        exit(-1);  # プログラムの終了


    # ------------各サイトへのログインチェック------------

    # netseaスクレイピングライブラリのインスタンス化
    netsea = MyNetseaLib.MyNetseaLib(browser, DEBUGMODE)  # netseaライブラリの呼び起こし
    #ログインチェック。ログインしていなければログインを催促
    netsea.loginCheck()

    # PETポチっとスクレイピングライブラリのインスタンス化
    petpochitto = MyPetpochittoLib.MyPetpochittoLib(browser, DEBUGMODE)#netseaライブラリの呼び起こし
    #ログインチェック。ログインしていなければログインを催促
    petpochitto.loginCheck()

    # 卸売りドットコム
    oroshiuri = MyOroshiuriLib.MyOroshiuriLib(browser, DEBUGMODE)  # netseaライブラリの呼び起こし
    #ログインチェック。ログインしていなければログインを催促
    oroshiuri.loginCheck()

    # スーパーデリバリー
    superdelivery = MySuperdeliveryLib.MySuperdeliveryLib(browser, DEBUGMODE)  # netseaライブラリの呼び起こし
    # ログインチェック。ログインしていなければログインを催促
    superdelivery.loginCheck()

    # タジマヤ卸ネット
    tajimayaoroshi = MyTajimayaoroshiLib.MyTajimayaoroshiLib(browser, DEBUGMODE)  # netseaライブラリの呼び起こし
    # ログインチェック。ログインしていなければログインを催促
    tajimayaoroshi.loginCheck()


    print("スクレイピングを開始します")

    #0からjancode_listの最大値まで操作。実際の行番号は2からなので転記時は+2する
    #列とサイトの対応表は以下の通り(配列と対応のため0開始,計20列)
    # NETSEA:15
    # PETポチッと:16
    # 卸売ドットコム:17
    # スーパーデリバリー:18
    # タジマヤ:19

    for item_count in range(len(jancode_list)):
        print(f"■■■スクレイピング対象：{jancode_list[item_count]}■■■■■■■■■■■■")

        #item_count行の列数が15列未満の場合、列を追加して整える。
        #既に価格登録がある場合、取得せずそのままの値を戻す。
        while len(jancode_list[item_count]) < 20:
            jancode_list[item_count].append("")

        #JANコードが適正かチェック
        jancode = jancode_list[item_count][0]
        if MyReg.isMatchPattern(r'^\d{11}$', jancode):
            msg = f"【致命的なエラー】JANコードが不正です({jancode_list[item_count][0]})"
            print('\033[31m' + msg + '\033[0m')
            myerror.myError(msg, status='error')
            #このJANはスキップ
            continue


        #①NETSEAから価格を取得=================================================================================================================
        # （price=[1000,'https://www.netsea.jp/shop/594530/4562350988125']
        #もし15列目が空ならNETSEAから価格を取得
        netsea_price = ["", ""]
        if jancode_list[item_count][15] != "":
            print(f"NETSEAは価格入力があるためスキップ[{jancode_list[item_count][0]},{jancode_list[item_count][1]}]")
        else:
            try:
                netsea_price = netsea.getPriceByJancode(jancode_list[item_count][0])
                print(f"main:{jancode_list[item_count][0]}の結果(NETSEA):",end="")
                print(netsea_price)
                #jancode_list[item_count][15] = netsea_price[0]
            except Exception as e:
                msg = f"【致命的なエラー】NETSEAからJAN{jancode_list[item_count][0]}の価格取得に失敗しました。処理をスキップします。error:" + str(e)
                print('\033[31m' + msg + '\033[0m')
                if DEBUGMODE:  # tracebackの表示
                    print(traceback.format_exc())
                myerror.myError(msg, status='error')


        #②PETポチッとから価格を取得=================================================================================================================
        # （price=[1000,'https://www.netsea.jp/shop/594530/4562350988125']
        # もし16列目が空ならPETポチッとから価格を取得
        petpochitto_price = ["", ""]
        if jancode_list[item_count][16] != "":
            print(f"PETポチッとは価格入力があるためスキップ[{jancode_list[item_count][0]},{jancode_list[item_count][1]}]")
        else:
            try:
                petpochitto_price = petpochitto.getPriceByJancode(jancode_list[item_count][0])
                print(f"main:{jancode_list[item_count][0]}の結果(PETポチッと):", end="")
                print(petpochitto_price)
                #jancode_list[item_count][16] = petpochitto_price[0]
            except Exception as e:
                msg = f"【致命的なエラー】PETポチッとからJAN{jancode_list[item_count][0]}の価格取得に失敗しました。処理をスキップします。error:" + str(
                    e)
                print('\033[31m' + msg + '\033[0m')
                if DEBUGMODE:  # tracebackの表示
                    print(traceback.format_exc())
                myerror.myError(msg, status='error')


        # ③卸売ドットコムから価格を取得=================================================================================================================
        # （price=[1000,'https://www.netsea.jp/shop/594530/4562350988125']
        # もし17列目が空なら卸売ドットコムからから価格を取得
        oroshiuri_price = ["", ""]
        if jancode_list[item_count][17] != "":
            print(f"卸売ドットコムは価格入力があるためスキップ[{jancode_list[item_count][0]},{jancode_list[item_count][1]}]")
        else:
            try:
                oroshiuri_price = oroshiuri.getPriceByJancode(jancode_list[item_count][0])
                print(f"main:{jancode_list[item_count][0]}の結果(卸売ドットコム):", end="")
                print(oroshiuri_price)
                #jancode_list[item_count][17] = oroshiuri_price[0]
            except Exception as e:
                msg = f"【致命的なエラー】卸売ドットコムからJAN{jancode_list[item_count][0]}の価格取得に失敗しました。処理をスキップします。error:" + str(
                    e)
                print('\033[31m' + msg + '\033[0m')
                if DEBUGMODE:  # tracebackの表示
                    print(traceback.format_exc())
                myerror.myError(msg, status='error')


        # ④スーパーデリバリーから価格を取得=================================================================================================================
        # （price=[1000,'https://www.netsea.jp/shop/594530/4562350988125']
        # もし18列目が空ならスーパーデリバリーから価格を取得
        superdelivery_price = ["", ""]
        if jancode_list[item_count][18] != "":
            print(f"スーパーデリバリーは価格入力があるためスキップ[{jancode_list[item_count][0]},{jancode_list[item_count][1]}]")
        else:
            try:
                superdelivery_price = superdelivery.getPriceByJancode(jancode_list[item_count][0])
                print(f"main:{jancode_list[item_count][0]}の結果(スーパーデリバリー):", end="")
                print(superdelivery_price)
                #jancode_list[item_count][18] = superdelivery_price[0]
            except Exception as e:
                msg = f"【致命的なエラー】スーパーデリバリーからJAN{jancode_list[item_count][0]}の価格取得に失敗しました。処理をスキップします。error:" + str(
                    e)
                print('\033[31m' + msg + '\033[0m')
                if DEBUGMODE:  # tracebackの表示
                    print(traceback.format_exc())
                myerror.myError(msg, status='error')



        # ➄タジマヤ卸ネットから価格を取得=================================================================================================================
        # （price=[1000,'https://www.netsea.jp/shop/594530/4562350988125']
        # もし19列目が空ならスーパーデリバリーから価格を取得
        tajimayaoroshi_price = ["", ""]
        if jancode_list[item_count][19] != "":
            print(
                f"タジマヤ卸ネットは価格入力があるためスキップ[{jancode_list[item_count][0]},{jancode_list[item_count][1]}]")
        else:
            try:
                tajimayaoroshi_price = tajimayaoroshi.getPriceByJancode(jancode_list[item_count][0])
                print(f"main:{jancode_list[item_count][0]}の結果(タジマヤ卸ネット):", end="")
                print(tajimayaoroshi_price)
                #jancode_list[item_count][19] = tajimayaoroshi_price[0]
            except Exception as e:
                msg = f"【致命的なエラー】タジマヤ卸ネットからJAN{jancode_list[item_count][0]}の価格取得に失敗しました。処理をスキップします。error:" + str(
                    e)
                print('\033[31m' + msg + '\033[0m')
                if DEBUGMODE:  # tracebackの表示
                    print(traceback.format_exc())
                myerror.myError(msg, status='error')


        #スプシを更新
        sheets.setws("【セラーID】リサーチ商品群")
        #sheets.update("F"+str(item_count+2)+":Y"+str(item_count+2),[jancode_list[item_count]])
        # 15列netseaにurlをセット
        if netsea_price[0] != "":
            sheets.update_add_hyperlink("U"+str(item_count+2),netsea_price[0],netsea_price[1])
        # 16列PETポチっとにurlをセット
        if petpochitto_price[0] != "":
            sheets.update_add_hyperlink("V"+str(item_count+2),petpochitto_price[0],petpochitto_price[1])
        # 17列卸売りドットコムにurlをセット
        if oroshiuri_price[0] != "":
            sheets.update_add_hyperlink("W"+str(item_count+2),oroshiuri_price[0],oroshiuri_price[1])
        # 18列スーパーデリバリーにurlをセット
        if superdelivery_price[0] != "":
            sheets.update_add_hyperlink("X"+str(item_count+2),superdelivery_price[0],superdelivery_price[1])
        # 19列タジマヤにurlをセット
        if tajimayaoroshi_price[0] != "":
            sheets.update_add_hyperlink("Y"+str(item_count+2),tajimayaoroshi_price[0],tajimayaoroshi_price[1])

        print("")

    # ==============終了処理(ブラウザの終了)===========================
    del browser
    del netsea
    del petpochitto
    del oroshiuri
    del superdelivery
    del tajimayaoroshi
