import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import ssl
import pytz
import sys
import re
from util.config_reader import load_config
from util.mail_module import connect_to_email_server, filter_emails_by_subject, extract_text_from_email
from util.backlog_module import fetch_backlog_tickets, fetch_backlog_comments, summarize_tickets, invert_dicｔ, remove_empty_lines
from util.nippo import Nippo

config = load_config()

# GmailのIMAPサーバー情報
IMAP_SERVER = config["IMAP_SERVER"]
IMAP_PORT = config["IMAP_PORT"]
EMAIL_ACCOUNT = config["EMAIL_ACCOUNT"]  # 自分のGmailアドレス
PASSWORD = config["PASSWORD"]  # アプリパスワードを使用（通常のパスワードではなく、2段階認証のアプリパスワード）
# BacklogのAPI設定
API_KEY = config["BACKLOG_API_KEY"]
BACKLOG_SPACE = config["BACKLOG_SPACE"] 
PROJECT_DICT = config["PROJECT_DICT"] 

# Gmailへ下書きを作成する。
def create_draft(subject, body):    
    # メールの作成
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = 'k@s-cubism.jp, d_system_support@s-cubism.jp'  # 宛先
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

def main():
    # 現在の日付時刻を取得してパラメータとしてセット
    now = datetime.now()
    target_date =  now.strftime('%Y-%m-%d')
    start_time = "xx:xx"
    current_time = now.strftime("%H:%M")
    
    # nippoクラスを作成
    nippo = Nippo()
    
    keyword_regex = "^【勤怠連絡】\d{4}/\d{1,2}/\d{1,2} [日月火水木金土] 二條 (リモート|出社)$"
    mail = connect_to_email_server(EMAIL_ACCOUNT, PASSWORD)
    filtered_emails = filter_emails_by_subject(mail, 7, folder = "[Gmail]/&kAFP4W4IMH8w4TD8MOs-", keyword_regex = keyword_regex)
    subjects = filtered_emails[1]
    print(subjects)
    if len(filtered_emails[0]):
        extracted_text = extract_text_from_email(filtered_emails[0][-1])
        
        startTimePtn = r'開始[\s:](\d{1,2}:\d{1,2})'
        match = re.search(startTimePtn, extracted_text)
        
        if match:
            start_time = match[1]
        
        print(extracted_text)
        print(start_time)
        
        pattern = r'▼[\s\S]*?(?=▼|$)'
        match = re.search(pattern, extracted_text)
        
        if match:
            extracted_text = match.group().strip()
        
    body = f"\n本日の業務を終了します。\n\n開始:{start_time} - 終了:{current_time} \n\n{extracted_text}\n\n▼その他\nチケット発生都度対応"
    # print(body)
    nippo.addTxt(extracted_text)
    
    # backlogの当日の情報を取得
    backlogTxt = ""
    projects = invert_dict(PROJECT_DICT)
    for name, projectIds in projects.items():
        backlogTxt += f"▼{name}\n"
        for project_id in projectIds:
            tickets = fetch_backlog_tickets(date=target_date, project_id=project_id)               
            if not tickets:
                print(f"{name}(project_id:{project_id}) No tickets found for the specified date:{target_date}")
                continue
            
            # チケットの要約を生成
            summaries = summarize_tickets(tickets, target_date)
            for ticket_key, summary in summaries.items():
                backlogTxt += f"・{ticket_key} {summary['summary']}\n"
                for date, comment in summary['comments'].items():
                    backlogTxt +=f"→{date}:\n"
                    backlogTxt +=f"{remove_empty_lines(comment)}\n"

    print(nippo.exportText())


if __name__ == "__main__":
    if len(sys.argv) > 1:
     # 最初の要素はスクリプト名なので、それ以降を取得
     if sys.argv[1] == "s":
         remoteFlg = False
    main()

# python3 nippo_gen.py s
