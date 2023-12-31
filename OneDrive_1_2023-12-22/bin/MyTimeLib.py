# coding: utf-8

# -----------------------------------
# メルカリ再出品スクリプトメインプログラム
# 　制作2022.11.16
# -----------------------------------
from time import time
from time import sleep
import random
import datetime

def getWeekday():
    # 今日の曜日を取得する 月曜日を表す0から、日曜日を表す6までの値で取得できます。
    today = datetime.date.today()
    weekdayNum = today.weekday()
    if weekdayNum == 0:
        weekdayStr = "月曜日"
    elif weekdayNum == 1:
        weekdayStr = "火曜日"
    elif weekdayNum == 2:
        weekdayStr = "水曜日"
    elif weekdayNum == 3:
        weekdayStr = "木曜日"
    elif weekdayNum == 4:
        weekdayStr = "金曜日"
    elif weekdayNum == 5:
        weekdayStr = "土曜日"
    elif weekdayNum == 6:
        weekdayStr = "日曜日"

    print("今日は" + weekdayStr + "です")
    return weekdayStr

#現在時刻の取得
def getTime():
    dt = datetime.datetime.now()# ローカルな現在の日付と時刻を取得
    # 日付と時刻を構成する要素の取り出し
    return datetime.time(dt.hour, dt.minute, 00)

#datetime.time形式に指定分を足す
def addMinutesToTime(basetime,  minutes=0, seconds=0):
    dt = datetime.datetime.combine(datetime.date.today(), basetime)+ datetime.timedelta(minutes=minutes) + datetime.timedelta(seconds=seconds)
    return datetime.time(dt.hour, dt.minute, dt.second)

#現在日時、時刻の取得
def getDatetimeNow():
    return datetime.datetime.now()# UNIXタイムに基づくローカルな現在の日付と時刻(2023.7.12 16:23:22)を取得

# ボット対策のために前回のアクセスから指定時間待機するwaitメソッドを管理するクラス,日付をまたいだ際の対策済み
WAITTIMEARG=10
class MyWait():
    def __init__(self):
        dt = datetime.datetime(2023, 1, 1, 0, 0, 0)# 時間の初期値を2023/1/1 0:0:0に設定
        self.last_request_ime = dt.timestamp()

    #前回のwaitからinterval秒待機する。randumSecondが指定された場合、randumSecond秒ランダムに追加する
    def wait(self, interval=WAITTIMEARG, randumSecond=0):
        # 現在時間から最後のリクエスト時間を引く。もし指定秒未満だった場合、指定秒になるまでwait
        wait_time = self.last_request_ime - time() + interval

        if (wait_time > 0.0):

            if(randumSecond>0):
                randumNum = (random.random() * randumSecond*2) -randumSecond
                wait_time += randumNum
                if(wait_time<0):
                    wait_time = 0.3

            #分の計算
            minutes = int(wait_time/60)

            #分が1以上なら表示
            if minutes > 0:
                print(f"連続アクセス回避のため{minutes}分{int(wait_time % 60)}秒間待機します")
            else:
                print(f"連続アクセス回避のため{wait_time}秒間待機します")

            sleep(wait_time)

        self.last_request_ime = time()


# ----------------------------
# メインここから
# ----------------------------
if __name__ == '__main__':
    wait = MyWaint()
    print(f"lastRequestTime={wait.lastRequestTime}")
    sleep(5)
    print(time())
    wait.wait(interval=1, randumSecond=10)
