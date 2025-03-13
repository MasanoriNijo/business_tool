# config_reader.py
import json
import imaplib
from datetime import datetime, timedelta
import email
from email.header import decode_header
import ssl
import re
import copy

# 日報の情報を構造化,取込および出力するクラス
class Nippo:

    def __init__(self):
        self.data = {}  

    def addTxt(self, txt, biko=""):
        mailTxts = []
        for item in txt.split("\n"):
            item = item.strip()
            item = item.strip("\n")
            item = item.strip("\r")
            if item:
                mailTxts.append(item)
        finRegex = "\d{4}年\d{1,2}月\d{1,2}日\([日月火水木金土]\) \d{1,2}:\d{1,2}" # 2024年9月12日(木) 10:43 二條正則 <masanori.nijo@s-cubism.jp>: のところで終わりにする。
        komokuRegexs = ["▼","・","→",finRegex]
        
        startFlg = False # 記載対象が始まったらTrue
        ind = 0 # 現在の位置
        buf = [] # 一時的に保持
        for mltxt in mailTxts:
            if startFlg:
                matchedFlg = False    
                for ind_ in range(4):
                    match = re.match("^" + komokuRegexs[ind_] + "(.*)", mltxt)
                    if match:
                        matchedFlg = True        
                        if ind < ind_ and ind_ < 3:
                            buf.append(match[1].strip())
                            ind += 1
                        elif ind == ind_:
                            # 追加する。

                            self._buf_add_to_nippo(buf, biko)
                            # bufを戻す。
                            buf.pop()
                            buf.append(match[1].strip())
                        elif ind_ < 3:
                            # 追加する。       
                            self._buf_add_to_nippo(buf, biko)
                            # bufを戻す。
                            while ind >= ind_:
                                buf.pop()
                                ind -= 1
                            buf.append(match[1].strip())
                            ind += 1
                        else: # 追記対象の最後を感知した場合。
                            # 最後を追加する。そして処理を抜ける。
                            self._buf_add_to_nippo(buf, biko) 
                            return
                        break
                if not matchedFlg:
                    # この場合は改行に内容が書かれている場合なので、追記する。
                    buf[-1] += mltxt
            else: # 処理対象の始まりを判定する
                match = re.match("^" + komokuRegexs[0] + "(.*)", mltxt)
                if match:
                    startFlg = True
                    buf.append(match[1].strip())
                    ind = 0
        if startFlg:
            # 最後を追加する。そして処理を抜ける。
            self._buf_add_to_nippo(buf, biko) 
    
    # テキストの内容を成型してデータ構造として保持する。
    def _buf_add_to_nippo(self, buf, biko = ""):
        # 追加する。
        buf_ = copy.deepcopy(buf)
        while len(buf_) < 3:
            buf_.append("N")  
        buf_[0] = buf_[0].replace("　", " ")
        buf_[1] = buf_[1].replace("　", " ")
        buf_[2] = buf_[2].replace("　", " ")
        if buf_[0] not in self.data:
            self.data[buf_[0]] = {}
        if buf_[1] not in self.data[buf_[0]]:
            self.data[buf_[0]][buf_[1]] = []
        if buf_[2] not in self.data[buf_[0]][buf_[1]]:
            self.data[buf_[0]][buf_[1]].append(buf_[2] + biko)
    
    def exportText(self):
        return self._exportDataRecursive(self.data)

    # nippoデータをテキスト出力する。
    def _exportDataRecursive(self, nippo, outTxt:str = '', lvl:int = 0):   
        points = ['▼','・',' →','','']
        if type(nippo) is dict:
            for key, value in nippo.items():
                if lvl < 2:
                    outTxt += '\n'
                outTxt += points[lvl]
                outTxt += key
                if lvl > 0:
                    outTxt += '\n'
                outTxt = self._exportDataRecursive(value, outTxt, lvl + 1)
        elif type(nippo) is list:
            for value in nippo:
                outTxt += points[lvl]
                outTxt += value
                outTxt += '\n'
        return outTxt