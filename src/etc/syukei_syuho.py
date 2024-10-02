
import requests
import json
import random
import time
import sys
import os
import re
import json

sec1 = '^【週報】(.*)' # ex.【週報】8月第4週 二條 8月9日(金)～8月22日(木)
sec2 = '^▼(.*)' # ex. ▼イオンペット案件
sec3 = '^・(.*)' # ex. ・AEONPET_POS_CS-1002 レジごとの残置金（釣銭機残置額）の確認方法について
sec4 = '^→(.*)' # ex. →問い合わせ事項調査回答済(8/20)
points = ['▼','・','→','','']

pos = 0 #　現在のセクションポジション
secs = [sec1,sec2,sec3,sec4]
syuho = [] # [sec1,sec2,sec3,sec4,value]
syuhos = {} # 集計データ格納先

def writeTxt(txt:str,isAdd:bool):
    if isAdd:
        f = open('komati_qst.txt','a')
    else:
        f = open('komati_qst.txt','w')
    f.write(txt + '\n')
    f.close

def readTxt(path:str):
    f = open(path,'r', encoding='UTF-8')
    data = f.read()
    f.close
    return data

def syukei(path:str):
    path = os.path.dirname(__file__) + '\\' + path
    f = open(path,'r', encoding='UTF-8')
    addFlg = False
    data = ''
    while True:
        data_ = f.readline()
        if data_:
            ind = 0
            matchFlg = False
            for reg in secs:               
                match = re.match(reg,data_)
                if match:
                    matchFlg = True
                    if ind < 3:
                        if addFlg:
                            addData(syuho,data)
                            data = ''
                            addFlg = False
                        if len(syuho) < ind + 1:
                            syuho.append(match[1])
                        else:
                            syuho[ind] = match[1]
                        while len(syuho) > ind+ 1:
                            syuho.pop(-1)                        
                    else:
                        if len(data)>0 and addFlg:
                            addData(syuho,data)
                            data = ''
                        data = match[1].strip()
                        addFlg = True
                    break
                ind += 1
            if matchFlg == False:
                data += data_.strip()
        else:
            break        
    f.close

def addData(syuho,data:str):
    if syuho[1] not in syuhos:
       syuhos[syuho[1]] = {}
    if syuho[2] not in syuhos[syuho[1]]:
       syuhos[syuho[1]][syuho[2]] = []
    if data not in syuhos[syuho[1]][syuho[2]]:
        syuhos[syuho[1]][syuho[2]].append(data)

def addData_all(syuho,data:str):
    if syuho[0] not in syuhos:
        syuhos[syuho[0]] = {}
    if syuho[1] not in syuhos[syuho[0]]:
       syuhos[syuho[0]][syuho[1]] = {}
    if syuho[2] not in syuhos[syuho[0]][syuho[1]]:
       syuhos[syuho[0]][syuho[1]][syuho[2]] = []
    syuhos[syuho[0]][syuho[1]][syuho[2]].append(data)
    
def exportDataRecursive(data, outTxt:str = '', lvl:int = 0):
    
    if type(data) is dict:
        for key, value in data.items():
            outTxt += '\n'
            outTxt += points[lvl]
            outTxt += key
            outTxt += '\n'
            outTxt = exportDataRecursive(value, outTxt, lvl + 1)
    elif type(data) is list:
        for value in data:
            outTxt += points[lvl]
            outTxt += value
            outTxt += '\n'
    return outTxt

# args = sys.argv
# path:str = args[1]
# syukei(path)

syukei('syuho_20240902.txt')

# jsonPath = os.path.dirname(__file__) + '\\' + 'syukei_syuho.json'
# jsonFile = open(jsonPath, mode="w")
# json.dump(syuhos, jsonFile)
# jsonFile.close()
# print(syuhos)

# jsonData = json.dumps(syuhos, ensure_ascii=False)
# print(jsonData)

outTxt = exportDataRecursive(syuhos)
print(outTxt)

