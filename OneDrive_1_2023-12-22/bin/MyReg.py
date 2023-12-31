# coding: utf-8

# -----------------------------------
# 正規表現ライブライ
# 　制作2022.12.20
# -----------------------------------

import re

#文字列から数字のみ抜き出す.結果空文字''となる場合がある。
def rtnNumFromStr(string):
    try:
        rtn_num = float(re.sub(r"[^0-9\.]", "", string))
    except Exception as e:
        rtn_num = ""

    return rtn_num

#正規表現に一致するパターンを返す　例rtnMatchPattern(r'[0-9]+位', "120位")
#サブマッチパターンを用いる場合　例rtnMatchPattern(r'([0-9]+)位', "120位", 1) 0を指定するとマッチした文字全体を返す
def rtnMatchPattern(pattern, content, gropu=0):
    if(pattern == ""):
        return None

    result = re.search(pattern, content)

    if result is None:
        return None
    else:
        return result.group(gropu)

#パターン正規表現に完全一致する場合Trueを返す 例：isMatchPattern(r'^([+-])?([0-9]+)(\.)?([0-9]+)?$', '11.5')
def isMatchPattern(pattern, content):
    if(re.fullmatch(pattern, content)is not None):
        return True

    else:
        return False

#パターンが文字列内に部分一致する場合Trueを返す。
def isSerchPattern(pattern, content):
    if(re.search(pattern, content)is not None):
        return True

    else:
        return False

# ----------------------------
# メインここから
# ----------------------------a
if __name__ == '__main__':
    str = "/sell/categories?category_id=22"
    str_match = rtnMatchPattern(r'id=(\d+)', str, 1)

    print(str_match)
    print(type(str_match))