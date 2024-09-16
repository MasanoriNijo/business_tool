from transformers import pipeline
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta

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
def filter_emails_by_subject(mail, folder="inbox", keyword_regex=".*"):
    mail.select(folder)
    
    # メール一覧を取得(全件)
    # result, data = mail.search(None, "ALL")
    
    # 直近N日分のメールを検索
    N = 7  # 例として直近7日間
    date_N_days_ago = (datetime.now() - timedelta(days=N)).strftime('%d-%b-%Y')

    # SINCEコマンドでN日前以降のメールを検索
    result, data = mail.search(None, f'SINCE {date_N_days_ago}')
    filtered_emails = []
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
    
    return filtered_emails

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
def exchange_text_to_nippo(mailTxt, nippo = {}):
    mailTxts = []
    for item in mailTxt.split("\r\n"):
        item = item.strip()
        if item:
            mailTxts.append(item)
    finRegex = "\d{4}年\d{1,2}月\d{1,2}日\([日月火水木金土]\) \d{2}:\d{2}" # 2024年9月12日(木) 10:43 二條正則 <masanori.nijo@s-cubism.jp>: のところで終わりにする。
    komokuRegexs = ["▼","・","→",finRegex]
    
    startFlg = False
    ind = 0
    buf = []
    for mltxt in mailTxts:
        if startFlg:
            for ind_ in range(4):
                match = re.match("^" + komokuRegexs[ind_] + "(.*)",mltxt)
                if match:
                    if ind < ind_ and ind_ < 3:
                        buf.append(match[1])
                        ind += 1
                    elif ind_ < 3:
                        # 追加する。       
                        if buf[0] not in nippo:
                            nippo[buf[0]] = {}
                        if buf[1] not in nippo[buf[0]]:
                            nippo[buf[0]][buf[1]] = []
                        if buf[2] not in nippo[buf[0]][buf[1]]:
                            nippo[buf[0]][buf[1]].append(buf[2])
                        # bufを戻す。
                        while ind >= ind_:
                            buf.pop()
                            ind -= 1
                        buf.append(match[1])
                        ind += 1
                    else:
                        # 最後を追加する。そして処理を抜ける。
                        while len(buf) < 3:
                            buf.append("N")      
                        if buf[0] not in nippo:
                            nippo[buf[0]] = {}
                        if buf[1] not in nippo[buf[0]]:
                            nippo[buf[0]][buf[1]] = []
                        if buf[2] not in nippo[buf[0]][buf[1]]:
                            nippo[buf[0]][buf[1]].append(buf[2])   
                        return nippo
                    break
            
            # この場合は改行に内容が書かれている場合なので、追記する。
            if ind == 2:
                buf[ind] += mltxt
        else:
            match = re.match("^" + komokuRegexs[0] + "(.*)",mltxt)
            if match:
                startFlg = True
                buf.append(match[1])
                nippo[match[1]]={}
                ind = 0
    return nippo
                
# テキスト記入
def append_text_to_file(text, filename):
    try:
        # 'a' モードでファイルを開く（ファイルがなければ作成される）
        with open(filename, 'a') as file:
            file.write(text + '\n')  # 指定されたテキストを追記
        print(f"'{text}' has been appended to {filename}.")
    except IOError as e:
        # 入出力エラーをキャッチ
        print(f"An I/O error occurred: {e}")

# nippoデータをテキスト出力する。
def exportDataRecursive(nippo, outTxt:str = '', lvl:int = 0):   
    points = ['▼','・','→','','']
    if type(nippo) is dict:
        for key, value in nippo.items():
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
def main(username, password, keyword_regex):
    # 1. メールサーバーに接続
    mail = connect_to_email_server(username, password)
    
    # 2. 件名でフィルタリング
    # filtered_emails = filter_emails_by_subject(mail, folder = "'[Gmail]/Sent Mail'", keyword_regex=keyword_regex)
    filtered_emails = filter_emails_by_subject(mail, folder = "[Gmail]/&kAFP4W4IMH8w4TD8MOs-", keyword_regex=keyword_regex)
    
    # 3. フィルタされたメールの本文を抽出
    extracted_texts = [extract_text_from_email(email) for email in filtered_emails]
    
    nippo = {}
    for extracted_text in extracted_texts:
        # append_text_to_file(extracted_text, "nippou.txt")
        nippo = exchange_text_to_nippo(extracted_text, nippo)
        
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
    
    # 実行
    main(username, password, keyword_regex)
