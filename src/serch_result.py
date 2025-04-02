from transformers import pipeline
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
import sys
import copy
import subprocess
from util.file_text_module import read_file
import json

from util.mail_module import connect_to_email_server, filter_emails_by_subject, extract_text_from_email

from util.config_reader import load_config
config = load_config()

# テキストの内容を成型してデータ構造として保持する。
def _buf_add_to_nippo(buf, nippo, date = ""):
    # 追加する。
    buf_ = copy.deepcopy(buf)      
    while len(buf_) < 3:
        buf_.append("N")  
    if buf_[0] not in nippo:
        nippo[buf_[0]] = {}
    if buf_[1] not in nippo[buf_[0]]:
        nippo[buf_[0]][buf_[1]] = []
    if buf_[2] not in nippo[buf_[0]][buf_[1]]:
        nippo[buf_[0]][buf_[1]].append(buf_[2] + date)

def exchange_text_to_nippo(mailTxt, nippo = {}, date = ""):
    mailTxts = []
    for item in mailTxt.split("\r\n"):
        item = item.strip()
        item = item.strip("\n")
        item = item.strip("\r")
        if item:
            mailTxts.append(item)
    finRegex = "〇BackLog実績" # 〇BackLog実績: のところで終わりにする。
    komokuRegexs = ["▼","・","→",finRegex]
    
    startFlg = False # 記載対象が始まったらTrue
    ind = 0 # 現在の位置
    buf = [] # 一時的に保持
    for mltxt in mailTxts:
        if startFlg:
            matchedFlg = False
            for ind_ in range(4):
                match = re.match("^" + komokuRegexs[ind_] + "(.*)",mltxt)
                if match:
                    matchedFlg = True        
                    if ind < ind_ and ind_ < 3:
                        buf.append(match[1].strip())
                        append_text_to_file(mltxt, f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_ALL_FILE']}")      
                        ind += 1
                    elif ind == ind_:
                        # 追加する。       
                        _buf_add_to_nippo(buf, nippo, date)
                        # bufを戻す。
                        buf.pop()
                        buf.append(match[1].strip())
                        append_text_to_file(mltxt, f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_ALL_FILE']}")      
                    elif ind_ < 3:
                        # 追加する。       
                        _buf_add_to_nippo(buf, nippo, date)
                        # bufを戻す。
                        while ind >= ind_:
                            buf.pop()
                            ind -= 1
                        buf.append(match[1].strip())
                        append_text_to_file(mltxt, f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_ALL_FILE']}")      
                        ind += 1
                    else: # 追記対象の最後を感知した場合。
                        # 最後を追加する。そして処理を抜ける。
                        _buf_add_to_nippo(buf, nippo, date) 
                        return nippo
                    break
            if not matchedFlg:
                # この場合は改行に内容が書かれている場合なので、追記する。
                buf[-1] += mltxt
        else: # 処理対象の始まりを判定する
            match = re.match("^" + komokuRegexs[0] + "(.*)", mltxt)
            if match:
                startFlg = True
                buf.append(match[1].strip())
                append_text_to_file(mltxt, f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_ALL_FILE']}")      
                ind = 0
    return nippo
                
# テキスト記入
def append_text_to_file(text, filename, msg = False):
    try:
        # 'a' モードでファイルを開く（ファイルがなければ作成される）
        with open(filename, 'a') as file:
            file.write(text + '\n')  # 指定されたテキストを追記
        # print(f"'{text}' has been appended to {filename}.")
        
        if msg:
            print(f"書き込み完了:path {filename}")

    except IOError as e:
        # 入出力エラーをキャッチ
        print(f"An I/O error occurred: {e}")

# nippoデータをテキスト出力する。
def exportDataRecursive(nippo, outTxt:str = '', lvl:int = 0):   
    points = ['▼','・',' →','','']
    if type(nippo) is dict:
        for key, value in nippo.items():
            if lvl < 2:
                outTxt += '\n'
            outTxt += points[lvl]
            outTxt += key
            if lvl > 0:
                outTxt += '\n'
            outTxt = exportDataRecursive(value, outTxt, lvl + 1)
    elif type(nippo) is list:
        for value in nippo:
            outTxt += points[lvl]
            outTxt += value
            outTxt += '\n'
    return outTxt

# AI要約用の関数
def ai_summarize_texts(texts, max_length=150):
    summarizer = pipeline("summarization")  # Hugging Faceの要約パイプライン
    combined_text = " ".join(texts)  # すべてのメール本文を結合
    
    # 要約を実行（モデルは長すぎる入力を処理できないため、適切な長さに制限）
    summary = summarizer(combined_text, max_length=max_length, min_length=30, do_sample=False)
    
    return summary[0]['summary_text']

# メイン処理
def main(read_file_path):

    # project_hokkoku-orange_base_server\data\class\SC_Product.php:
    #    493                            FROM dtb_products_class
    #    494:                           GROUP BY product_id
    #    495                          ) AS T1 ON T0.product_id = T1.product_id

    reg1 = r"^((.+)):"
    reg2 = r"   (\d*:?)(.*)"
    
    state = 0
    sel_key = ''
    sel_key2 = 0
    results = {}
    
    # read data
    data_text = read_file(read_file_path)
    data_texts = re.split(r"\r?\n", data_text)

    for txt_line in data_texts:
        print(results)
        match1 = re.match(reg1,txt_line)
        match2 = re.match(reg2,txt_line)
        match state:
            case 0:
                if match1:
                    results[txt_line] = {}
                    sel_key = txt_line
                state = 1
            case 1:
                if match2:
                    if not sel_key2 in results[sel_key]:
                        results[sel_key][sel_key2] = []
                    print("AAA")
                    print(results)
                    results[sel_key][sel_key2].append(txt_line)
                    print("BBB")
                    print(results)
                    continue
                if match1:
                    results[txt_line] = {}
                    sel_key = txt_line
                    sel_key2 = 0
                    continue
                sel_key2 +=1

    print(results)

    # matchs = re.findall(dataRegex,data_text)
    # JSON 形式の文字列に変換
    # json_str = json.dumps(matchs, ensure_ascii=False, indent=4)

    # 結果を表示
    # print(json_str)
    # print(matchs)

if __name__ == "__main__":

    read_file_path = "../in/search_result.txt"
    if len(sys.argv) > 1:
        # 最初の要素はスクリプト名なので、それ以降を取得
        read_file_path = sys.argv[1]

    # 実行
    main(read_file_path)
    
# 使い方
# vsCodeで検索した際の結果ファイルを読み込むツール
# python3 serch_result.py <読み込むファイルパス>
 