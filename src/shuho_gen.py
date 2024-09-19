from transformers import pipeline
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import re
from datetime import datetime, timedelta
import sys
import ssl
import pytz
import copy
import subprocess

from config_reader import load_config
config = load_config("C:/Users/masanori.nijo/Documents/chatGpt/src/config.json")
IMAP_SERVER = config["IMAP_SERVER"]
IMAP_PORT = config["IMAP_PORT"]
EMAIL_ACCOUNT = config["EMAIL_ACCOUNT"]  # 自分のGmailアドレス
PASSWORD = config["PASSWORD"]  # アプリパスワードを使用（通常のパスワードではなく、2段階認証のアプリパスワード）

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
def filter_emails_by_subject(mail, n_days_ago, folder="inbox", keyword_regex=".*", is_newest_first = False, max_cnt = -1):
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
        if is_newest_first:
            # 新しい順にするためにリストを逆にする
            email_ids = email_ids[::-1]
        
        cnt_ = 0
        
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
                        cnt_+=1
            if cnt_ == max_cnt:
                break
    
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

def exchange_text_to_nippo(mailTxt, nippo = {}, date = "", finRegex = "xxxx_nasi_xxxx"):
    mailTxts = []
    for item in mailTxt.split("\r\n"):
        item = item.strip()
        item = item.strip("\n")
        item = item.strip("\r")
        if item:
            mailTxts.append(item)
    komokuRegexs = ["▼","・","→",finRegex]
    
    startFlg = False # 記載対象が始まったらTrue
    ind = 0 # 現在の位置
    buf = [] # 一時的に保持
    for mltxt in mailTxts:
        if startFlg:
            matchedFlg = False
            append_text_to_file(mltxt, f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_ALL_FILE']}")      
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
    _buf_add_to_nippo(buf, nippo, date) # 最終行まで処理をするので、最後に追記する。
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
            if lvl > 0:
                outTxt += '\n'
            outTxt = exportDataRecursive(value, outTxt, lvl + 1)
    elif type(nippo) is list:
        for value in nippo:
            if value != "N":
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

from datetime import datetime

# 指定の日付x月y日が今日から何日前かを計算 
def days_ago(x, y, same_year = True, endFlg = False):
    # 今日の日付
    today = datetime.today()

    # 今年のx月y日を取得
    if same_year:
        input_date = datetime(today.year, x, y)
    else:
        input_date = datetime(today.year - 1, x, y)

    # 今日の日付との差を計算
    delta = today - input_date

    # 結果を表示
    if delta.days >= 0 or endFlg:
        return delta.days
    
    # 年をまたいでいるので再度計算
    return days_ago(x, y, False, True)

def create_draft(subject, body, pattern):
    """Gmailに下書きを作成する関数"""
    
    # メールの作成
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = ''  # 宛先
    msg['Subject'] = subject

    # メール本文を追加
    msg.attach(MIMEText(body, 'plain'))

    # メールをIMAPサーバに送信
    try:
        # SSLコンテキストを作成してIMAPサーバに接続
        context = ssl.create_default_context()
        with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context) as mail:
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            mail.select('inbox')  # 'inbox'フォルダを選択（必要に応じて変更）

            # メールデータの変換
            raw_message = msg.as_string()
            
            # タイムゾーンを含んだ現在日時（aware datetime）
            tz = pytz.timezone('Asia/Tokyo')  # 自分のタイムゾーンに合わせて変更
            now = datetime.now(tz)

            # 下書きフォルダに保存
            result = mail.append('[Gmail]/&Tgtm+DBN-', '\\Draft', imaplib.Time2Internaldate(now), raw_message.encode('utf-8'))
                
            if result[0] == 'OK':
                print("下書きを作成しました")
            else:
                print(f"下書きの作成に失敗しました: {result}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        
def create_draft_html(subject, body, pattern):
 
    # メールの作成
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = ''  # 宛先
    msg['Subject'] = subject

    # 正規表現にマッチした部分を赤色に変更
    def highlight_match(match):
        return f'<span style="color:red;">{match.group()}</span>'
    body_html = re.sub(pattern, highlight_match, body)
    body_html =  body_html.replace("\n","<br>")
    body_html =  body_html.replace("@@@","")
    
    # HTMLフォーマットのメールを作成
    body_html = f"""
    <html>
        <body>
            <p>{body_html}</p>
        </body>
    </html>
    """
    # メール本文を追加
    msg.attach(MIMEText(body_html, 'html'))

    # メールをIMAPサーバに送信
    try:
        # SSLコンテキストを作成してIMAPサーバに接続
        context = ssl.create_default_context()
        with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context) as mail:
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            mail.select('inbox')  # 'inbox'フォルダを選択（必要に応じて変更）

            # メールデータの変換
            raw_message = msg.as_string()
            
            # タイムゾーンを含んだ現在日時（aware datetime）
            tz = pytz.timezone('Asia/Tokyo')  # 自分のタイムゾーンに合わせて変更
            now = datetime.now(tz)

            # 下書きフォルダに保存
            result = mail.append('[Gmail]/&Tgtm+DBN-', '\\Draft', imaplib.Time2Internaldate(now), raw_message.encode('utf-8'))
                
            if result[0] == 'OK':
                print("下書きを作成しました")
            else:
                print(f"下書きの作成に失敗しました: {result}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

def get_japanese_weekday(date):
    # 曜日の英語表記から日本語表記へのマッピング
    weekday_map = {
        'Mon': '月',
        'Tue': '火',
        'Wed': '水',
        'Thu': '木',
        'Fri': '金',
        'Sat': '土',
        'Sun': '日'
    }
    
    # 現在の日付と曜日を取得
    english_weekday = date.strftime('%a')
    
    # 日本語の曜日を返す
    return weekday_map.get(english_weekday, '未知')

    
# メイン処理
def main(username, password):
     
    command2 = ['bash', '-c', 'echo "" > C:/Users/masanori.nijo/Documents/chatGpt/out/nippo_all.txt']
    # コマンドの実行
    subprocess.run(command2, check=True)
     
    # echo コマンドを実行してファイルを空にする
    command3 = ['bash', '-c', 'echo "" > C:/Users/masanori.nijo/Documents/chatGpt/out/nippo_matome.txt']
    # コマンドの実行
    subprocess.run(command3, check=True)
    
    sent_folder = "[Gmail]/&kAFP4W4IMH8w4TD8MOs-" # Gmailの送信済みフォルダ名
    
    # 1. メールサーバーに接続
    mail = connect_to_email_server(username, password)
    
    nippo = {}
    
    # 2. 前回の週報を取得する。
    keyword_regex = "^【週報】.*"
    n_days_ago = 30 # 直近の週報1件のみだが、便宜上30日前まで
    shuho_email_last = filter_emails_by_subject(mail, n_days_ago, folder = sent_folder, keyword_regex = keyword_regex, is_newest_first=True,max_cnt=1)
    subject = shuho_email_last[1]
    
    print(subject)
    append_text_to_file(subject[0], f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_ALL_FILE']}")
    
    # 3. 前回の週報の本文を抽出
    shuho_text = extract_text_from_email(shuho_email_last[0][0])
    fin_regex = "〇BackLog実績" # "〇BackLog実績"のところで終わりにする。
    nippo = exchange_text_to_nippo(shuho_text, nippo, "", fin_regex)

    # 4. 日報を取得
    
    keyword_regex = "^Re: 【勤怠連絡】.*"
    n_days_ago = 7 # 前回の週報の作成日から本日までの日数、便宜上7(一週間前)
    
    shuhoSubjectRegex = "^【週報】\d{1,2}月第\d週 \S+ \d{1,2}月\d{1,2}日\(.\)～(\d{1,2})月(\d{1,2})日\(.\) 週報$"
    match = re.match(shuhoSubjectRegex,subject[0]) # 【週報】9月第2週 二條 9月6日(金)～9月12日(木) 週報
    if match:
        n_days_ago = days_ago(int(match[1]),int(match[2]))
    nippo_emails = filter_emails_by_subject(mail, n_days_ago, folder = sent_folder , keyword_regex = keyword_regex)
    
    # 5. フィルタされた日報メールの本文を抽出
    nippo_texts = [extract_text_from_email(email) for email in nippo_emails[0]]
    subjects = nippo_emails[1]
    print(subjects)

    for ind, extracted_text in enumerate(nippo_texts):
        dateRegex = ".*\d{4}/(\d{1,2}/\d{1,2}).*"
        date = ""
        append_text_to_file("\n" + subjects[ind], f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_ALL_FILE']}")
        match = re.match(dateRegex, subjects[ind])
        if match:
            date = " (" + match[1].strip() + ")@@@" # @@@は後処理のメール下書きに成型時の赤文字に変換するための目印。
        fin_regex = "\d{4}年\d{1,2}月\d{1,2}日\([日月火水木金土]\) \d{1,2}:\d{1,2}" # 2024年9月12日(木) 10:43 二條正則 <masanori.nijo@s-cubism.jp>: のところで終わりにする。
        nippo = exchange_text_to_nippo(extracted_text, nippo, date, fin_regex)
        nippoTxt = exportDataRecursive(nippo)

    nippoTxt = exportDataRecursive(nippo)
    append_text_to_file(nippoTxt, f"{config['SRC_TO_OUT_PATH']}/{config['NIPPO_MATOME_FILE']}")
    
    # 6.Gmailの下書きの保存
    # 現在の日付時刻を取得して件名に反映
    now = datetime.now()
    current_month = now.strftime(f"%m")
    current_date = now.strftime(f"%m月%d日({get_japanese_weekday(now)})")  
    before = now - timedelta(days=n_days_ago-1)   
    before_date = before.strftime(f"%m月%d日({get_japanese_weekday(before)})")
    
    subject = f"【週報】{current_month}月第X週 二條 {before_date}～{current_date} 週報"
    body = f"\n今週の週報を送付します。\n\n〇トピックス\n・特になし\n\n〇案件状況報告\n{nippoTxt}\n〇BackLog実績\n"
    red_pattern = r"→.*@@@"
    create_draft(subject, body, red_pattern)

if __name__ == "__main__":
    # Gmailのユーザ名とアプリパスワード（Googleで2段階認証が有効の場合に必要）
    username = config["EMAIL_ACCOUNT"]
    password = config["PASSWORD"]
    
    # 実行
    main(username, password)
    
# 使い方
# python3 shuho_gen.py
 