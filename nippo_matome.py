from transformers import pipeline
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
import sys
import copy
import subprocess

# メールサーバに接続
def connect_to_email_server(username, password, imap_server="imap.gmail.com"):
    mail = imaplib.IMAP4_SSL(imap_server)
    
    try:
        mail.login(username, password)
        # 参照可能なフォルダ名を取得したい場合は、コメントアウト
        # status, folders = mail.list()
        # if status == "OK":
            # for folder in folders:
            #     print(folder.decode())
    except imaplib.IMAP4.error as e:
        print(f"ログイン失敗: {e}")
        raise
    
    return mail


# メールの件名を正規表現でフィルタリング
def filter_emails_by_subject(mail, n_days_ago, folder="inbox", keyword_regex=".*"):
    mail.select(folder)
    
    # メール一覧を取得(全件)
    # result, data = mail.search(None, "ALL")
    
    # 直近N日分のメールを検索
    N = int(n_days_ago)  
    date_N_days_ago = (datetime.now() - timedelta(days=N)).strftime('%d-%b-%Y')
    print(date_N_days_ago)
    # SINCEコマンドでN日前以降のメールを検索
    result, data = mail.search(None, f'SINCE {date_N_days_ago}')
    filtered_emails = []
    subjects = []
    if result == "OK":
        email_ids = data[0].split()
        for email_id in email_ids:
            result, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    
                    # 件名がエンコードされている場合デコード
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # 正規表現で件名フィルタリング
                    if re.search(keyword_regex, subject):
                        filtered_emails.append(msg)
                        subjects.append(subject)
    
    return [filtered_emails, subjects]

# メールの内容をテキストとして抽出
def extract_text_from_email(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # プレーンテキスト部分を抽出
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    try:
                        data_ = part.get_payload(decode=True).decode("utf-8")
                        return data_
                    except:
                        pass
    else:
        return msg.get_payload(decode=True).decode("utf-8")
    
    return ""

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
    finRegex = "\d{4}年\d{1,2}月\d{1,2}日\([日月火水木金土]\) \d{1,2}:\d{1,2}" # 2024年9月12日(木) 10:43 二條正則 <masanori.nijo@s-cubism.jp>: のところで終わりにする。
    komokuRegexs = ["▼","・","→",finRegex]
    
    startFlg = False # 記載対象が始まったらTrue
    ind = 0 # 現在の位置
    buf = [] # 一時的に保持
    for mltxt in mailTxts:
        if startFlg:
            matchedFlg = False
            append_text_to_file(mltxt, "nippou_all.txt")        
            for ind_ in range(4):
                match = re.match("^" + komokuRegexs[ind_] + "(.*)",mltxt)
                if match:
                    matchedFlg = True        
                    if ind < ind_ and ind_ < 3:
                        buf.append(match[1].strip())
                        ind += 1
                    elif ind == ind_:
                        # 追加する。       
                        _buf_add_to_nippo(buf, nippo, date)
                        # bufを戻す。
                        buf.pop()
                        buf.append(match[1].strip())
                    elif ind_ < 3:
                        # 追加する。       
                        _buf_add_to_nippo(buf, nippo, date)
                        # bufを戻す。
                        while ind >= ind_:
                            buf.pop()
                            ind -= 1
                        buf.append(match[1].strip())
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
                ind = 0
    return nippo
                
# テキスト記入
def append_text_to_file(text, filename):
    try:
        # 'a' モードでファイルを開く（ファイルがなければ作成される）
        with open(filename, 'a') as file:
            file.write(text + '\n')  # 指定されたテキストを追記
        # print(f"'{text}' has been appended to {filename}.")
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
def main(username, password, keyword_regex, n_days_ago = 7):
     
    # echo コマンドを実行してファイルを空にする
    command1 = ['bash', '-c', 'echo "" > nippou_xxx.txt']
    # コマンドの実行
    subprocess.run(command1, check=True)
     
    # echo コマンドを実行してファイルを空にする
    command2 = ['bash', '-c', 'echo "" > nippou_all.txt']
    # コマンドの実行
    subprocess.run(command2, check=True)
     
    # echo コマンドを実行してファイルを空にする
    command3 = ['bash', '-c', 'echo "" > nippou.txt']
    # コマンドの実行
    subprocess.run(command3, check=True)
    
    # 1. メールサーバーに接続
    mail = connect_to_email_server(username, password)
    
    # 2. 件名でフィルタリング
    # filtered_emails = filter_emails_by_subject(mail, folder = "'[Gmail]/Sent Mail'", keyword_regex=keyword_regex)
    filtered_emails = filter_emails_by_subject(mail, n_days_ago, folder = "[Gmail]/&kAFP4W4IMH8w4TD8MOs-", keyword_regex = keyword_regex)
    
    # 3. フィルタされたメールの本文を抽出
    extracted_texts = [extract_text_from_email(email) for email in filtered_emails[0]]
    subjects = filtered_emails[1]
    print(subjects)
    nippo = {}
    for ind, extracted_text in enumerate(extracted_texts):
        dateRegex = ".*\d{4}/(\d{1,2}/\d{1,2}).*"
        date = ""
        append_text_to_file("\n" + subjects[ind], "nippou_all.txt")
        match = re.match(dateRegex, subjects[ind])
        if match:
            date = " (" + match[1].strip() + ")"
        # append_text_to_file(extracted_text, "nippou.txt")
        nippo = exchange_text_to_nippo(extracted_text, nippo, date)
        nippoTxt = exportDataRecursive(nippo)
        subjects[ind]
        append_text_to_file(subjects[ind], "nippou_xxx.txt")
        append_text_to_file(nippoTxt, "nippou_xxx.txt")
        
    nippoTxt = exportDataRecursive(nippo)
    append_text_to_file(nippoTxt, "nippou.txt")
    
    # 4. 抽出されたテキストをAIでまとめる
    # ai_summary = ai_summarize_texts(extracted_texts)
    
    # print("AIによる要約されたテキスト: \n", ai_summary)

if __name__ == "__main__":
    # Gmailのユーザ名とアプリパスワード（Googleで2段階認証が有効の場合に必要）
    username = "masanori.nijo@s-cubism.jp"
    password = "11Me9900002"
    
    # 件名のフィルタリングキーワード（正規表現）
    keyword_regex = "^Re: 【勤怠連絡】.*"
    
    n_days_ago = 31
    if len(sys.argv) > 1:
        # 最初の要素はスクリプト名なので、それ以降を取得
        n_days_ago = sys.argv[1]

    # 実行
    main(username, password, keyword_regex, n_days_ago)
    
# 使い方
# python3 nippo_matome.py N (Nは過去何日分 省略した場合7 直近一週間分)
 