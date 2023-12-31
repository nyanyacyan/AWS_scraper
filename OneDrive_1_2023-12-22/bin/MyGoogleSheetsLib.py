# coding: utf-8

# -----------------------------------
# スプシに関するするツール
# 　制作2022.10.29
#参考；https://tanuhack.com/library-gspread/#i-9
# -----------------------------------
import gspread
from gspread_formatting import *
from gspread_formatting import cellFormat, color
from oauth2client.service_account import ServiceAccountCredentials
from bin import MyFileIOLib
# import MyFileIOLib

class MyGoogleSheetsLib():
    #sheetName = None
    wb = None #ワークブック
    ws = None
    #client = None
    SPREADSHEET_KEY = None


    # initialize-
    def __init__(self, spreadsheet_key_input = None):
        #スプレッドシートキーの取得
        if spreadsheet_key_input is None:
            self.SPREADSHEET_KEY = MyFileIOLib.readCsvFile("./APIKey/SPREADSHEET_KEY.txt")[0][0]
        else:
            self.SPREADSHEET_KEY = MyFileIOLib.readCsvFile("./APIKey/"+spreadsheet_key_input)[0][0]
        print("スプレッドシート:" + self.SPREADSHEET_KEY)

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('APIKey/client_secret.json', scope)
        client = gspread.authorize(creds)

        self.wb = client.open_by_key(self.SPREADSHEET_KEY)

    #指定したシートが存在するかチェック
    def is_exist_worksheet(self,name):
        try:
            self.wb.worksheet(name)
            # エラーが発生しない＝nameのシートが存在
            return True
        except Exception as e:
            # エラーが発生した= nameのシートが存在しない
            return False

    #シート名を指定してカレントシートを設定する
    def setws(self, name):
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        self.ws = self.wb.worksheet(name)

    #現在選択しているシートを指定した名称でコピー
    def copyws(self, name):
        ws_id = self.ws.id
        self.wb.duplicate_sheet(source_sheet_id = ws_id, new_sheet_name = name, insert_sheet_index = 2)


    #シートの値を取得する。引数はセル.入力例はgetValue('A2')
    def getValue(self,cell):
        # Extract and print all of the values
        #print(worksheet.acell('A2').value)
        return self.ws.acell(cell).value

    # シートの複数セルの値を取得する。引数はセル範囲.入力例はgetValue('A2:A2') getValue("A2:C2")2次元配列でリターン
    def getValues(self, cells):
        return self.ws.get(cells)

    #シートの値を上書きする。引数はセル、値,つかい方update('A1:B2', [[1, 2], [3, 4]]) update('B1', 'Bingo!')
    def update(self, cell, value): #
        #print("sheets.update:"+cell+",")
        #print(value)
        self.ws.update(cell, value,value_input_option='USER_ENTERED') #数式を文字列にしないようにするオプションhttps://www.tantan-biyori.info/blog/2019/11/pythongspread-formula.html

    #ハイパーリンクをつける
    def update_add_hyperlink(self, cell, link_text, link_url): #
        #print("sheets.update:"+cell+",")
        #print(value)
        # ハイパーリンクを設定
        hyperlink_formula = f'=HYPERLINK("{link_url}","{link_text}")'
        self.ws.update(cell, hyperlink_formula, value_input_option='USER_ENTERED') #数式を文字列にしないようにするオプションhttps://www.tantan-biyori.info/blog/2019/11/pythongspread-formula.html


    #指定した列のブランク行を取得（最終行の次の行を返す）使い方：next_available_row(1)
    def next_available_row(self, col):
        str_list = list(filter(None, self.ws.col_values(col)))
        return len(str_list) + 1

    # 指定した列のブランク行を取得（最終行の次の行を返す）使い方：next_available_row(1)
    def get_last_row(self, col):
        str_list = list(filter(None, self.ws.col_values(col)))
        return len(str_list)


    #最終行にデータを記載する items= ['Hello', 'here', 'is', 'Programmer', 'Life'], append_row(self, items, "G2"):
    # def append_row(self, items):
    #     print("sheets.append_row")
    #     print("items=", end="")
    #     print(items)
    #     #self.worksheet.append_row(items, table_range)
    #     self.ws.append_row(items)

    #指定したセルの色を変える
    #使い方setColor('A1:J1',color[1, 0, 0]) #RGB
    #RGBは　Red, Green, Blueのこと
    def setColor(self,cells,bgcolor):
        fmt = cellFormat(
            backgroundColor=color(bgcolor[0], bgcolor[1], bgcolor[2])
        )
        format_cell_range(self.ws, cells, fmt)

    #１行追加するindexを指定しない場合は最終行
    #使い方insert_row("text", index=10) ,insert_row(["text1", "text2"]) ,insert_row(["text1", "text2"], 10)
    def insert_row(self, text, index=-1):
        #もし配列でない場合は配列
        if not isinstance(text, list):
            text = [text]

        if(index==-1):
            self.ws.insert_row(text, index=10)
        else:
            self.ws.insert_row(text, index=index)


if __name__ == '__main__':
    sheets=MyGoogleSheetsLib()
    sheets.setws("商品リスト")
    last_row = sheets.get_last_row(1)
    values = sheets.getValues("A2:H" + str(last_row))
    print(values)