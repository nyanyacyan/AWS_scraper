# coding: utf-8

#-----------------------------------
#ファイル読み書き用ライブライ
#　制作2022.10.17
#  改定2023.04.21 export_encrypted_data,inport_encrypted_data関数を追記
#-----------------------------------
import traceback
import time
import os  # getcwd用
# from cryptography.fernet import Fernet
import json
import urllib.request
import shutil


#カンマ区切りのファイルを読み込む、引数はファイルまでのパス、一行目のインデックスがある場合はisIndex=True
def readCsvFile(path, isIndex=False):
    dataList = []  # コンデションリストの入れ物
    #print("isIndex=" + str(isIndex))

    try:
        with open(path, 'r', encoding='UTF-8') as file:
            # 全行取得
            lineList = file.readlines()
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        raise ValueError("csvファイルの読み込みに失敗しました。")
        return None

    if(isIndex):
        #print("1行目を削除しました。")
        del lineList[0] #インデックスである一行目を削除


    for line in lineList:
        # 行を改行コードを取り除いて取得
        line = line.replace("\n", "")
        strBuf = line.split(",")  # 0:0ID1,1:cate1,2:ID2,3:cate2,4:ID3,5:cate3
        dataList.append(strBuf)

    return dataList

#csvデータを書き出す
def wrightCsvFile(path,s):#line[行[列]の2次元配列
    try:
        with open(path, 'ab') as f:  # withは終了・エラー時に自動的にcloseメソッドが呼び出される
            # f.write(time.strftime('%Y/%m/%d %H:%M:%S '))

            #\xa0'()ノーブレークスペース等が含まれるとcp932への変換に失敗する。エラーを無視するオプションをつけて変換をする
            #参考：https://qiita.com/butada/items/33db39ced989c2ebf644
            s = s+'\n' #改行を追加
            b = s.encode('cp932', 'ignore')

            f.write(b)
            #print("wrightCsvFile")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        #raise ValueError("csvファイルの読み込みに失敗しました。")
        return False

    return True

#エラーログの出力
def errorLogger(exception, isPrint=False, path="./bin/errorLog.txt"):
    if(isPrint):
        print(str(exception) + traceback.format_exc())

    with open(path, 'a', encoding='utf-8') as f:  # withは終了・エラー時に自動的にcloseメソッドが呼び出される
        f.write(time.strftime('%Y/%m/%d %H:%M:%S '))
        f.write(str(exception) + traceback.format_exc())
        f.write('\n')

#ログの出力
def logger(text, isPrint=False, isTimestamp=False, path="./log.txt"):
    if(isPrint):
        print(text)

    with open(path, 'a', encoding='utf-8') as f:  # withは終了・エラー時に自動的にcloseメソッドが呼び出される
        if isTimestamp:
            f.write(time.strftime('%Y/%m/%d %H:%M:%S '))
        f.write(text)
        f.write('\n')

# 暗号化キーの保存場所
KEI_PATH = "./bin/key.key"
DATA_PATH = "./bin/data.dat"

#指定したファイルパスが存在するかのチェック.存在する場合はTrue,存在しない場合はFalseが返る
def check_existence(filePath):
    return os.path.isfile(filePath)

# URLを指定してファイルを取得する
def downloadAndRetunrFile(url):
    #403エラー対策。ユーザーエージェントの偽装（参考：https://self-development.info/%E3%80%90python%E3%80%91urllib-error-httperror%E3%81%AE%E8%A7%A3%E6%B1%BA%E6%96%B9%E6%B3%95/
    headers = {
        "User-Agent": "camouflage useragent",
    }

    request = urllib.request.Request(url=url, headers=headers)

    with urllib.request.urlopen(request) as web_file:
        data = web_file.read()
        return data

# URLを指定してファイルを開き、保存する。フォルダがない場合は作成する
def downloadAndSavefile(url, dst_path, fname):

    os.makedirs(dst_path, exist_ok=True)
    data = downloadAndRetunrFile(url)
    with open(dst_path + "/" + fname, mode='wb') as local_file:
        local_file.write(data)
        return True

#中身ごとdirectoryの削除
def deleteDirectory(path):
    if os.path.exists(path):#対象のディレクトリが存在するなら
        shutil.rmtree(path)
        return True
    else:
        return False

# #暗号化したデータを書き出す(dataはバイト型)
# def export_encrypted_data(byte_data):
#     #キーが既に存在する場合や読み込む
#     if(check_existence(KEI_PATH)):
#         with open(KEI_PATH, "rb") as test_key:
#             key = test_key.read()
#     #キーが存在しない場合は新しく作理保存する
#     else:
#         # キーを作成する
#         key = Fernet.generate_key()
#
#         # キーをローカルに保存する
#         with open(KEI_PATH, "wb") as key_data:
#             key_data.write(key)
#
#     # データをバイトに変換する
#     #byte_data = text.encode()
#
#     # Fernetオブジェクトの初期化
#     f = Fernet(key)
#
#     # バイトデータを暗号化する
#     encrypt_data = f.encrypt(byte_data)
#
#     # 暗号化した情報をファイルに書き込む
#     with open(DATA_PATH, "wb") as file:
#         file.write(encrypt_data)
#
# #暗号化したデータを読み込む(decrypt_dataはバイト型)
# def inport_encrypted_data():
#     #キーが既に存在する場合や読み込む
#     if(check_existence(KEI_PATH)):
#         with open(KEI_PATH, "rb") as test_key:
#             key = test_key.read()
#     #キーが存在しない場合は新しく作理保存する
#     else:
#         return None
#
#     # 暗号化したファイルの読み込み
#     with open(DATA_PATH, "rb") as file:
#         encryp_data = file.read()
#
#     # キーを使ってFernetオブジェクトを初期化
#     f = Fernet(key)
#     # データの復号化
#     decrypt_data = f.decrypt(encryp_data)
#
#     return decrypt_data
#
# #辞書型をバイト型に変換　参考：https://www.web-dev-qa-db-ja.com/ja/python/%E8%BE%9E%E6%9B%B8%E3%82%92%E3%83%90%E3%82%A4%E3%83%88%E3%81%AB%E5%A4%89%E6%8F%9B%E3%81%97%E3%80%81%E5%86%8D%E3%81%B3python%E3%81%AB%E6%88%BB%E3%82%8A%E3%81%BE%E3%81%99%E3%81%8B%EF%BC%9F/1041904931/
# def dict_to_binary(the_dict):
#     str = json.dumps(the_dict)
#     binary = ' '.join(format(ord(letter), 'b') for letter in str)
#     return binary.encode()
#
# #バイト型を辞書が他に変換
# def binary_to_dict(the_binary):
#     the_binary.decode()
#     jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
#     d = json.loads(jsn)
#     return d