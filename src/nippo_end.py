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
from util.file_text_module import save_text_to_file
import subprocess

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

def main():
    
    # echo コマンドを実行してファイルを空にする
    command2 = ['bash', '-c', 'echo "" > ../out/nippo_matome.txt']
    # コマンドの実行
    subprocess.run(command2, check=True)
    
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
    print(subjects[-1])
    if len(filtered_emails[0]):
        extracted_text = extract_text_from_email(filtered_emails[0][-1])
        print(extracted_text)
        
        startTimePtn = r'開始[\s:](\d{1,2}:\d{1,2})'
        match = re.search(startTimePtn, extracted_text)
        
        if match:
            start_time = match[1]
                
        pattern = r'▼[\s\S]*?(?=▼|$)'
        match = re.search(pattern, extracted_text)
        
        if match:
            extracted_text = match.group().strip()
        
    body = f"\n本日の業務を終了します。\n\n開始:{start_time} - 終了:{current_time} \n"
    nippo.addTxt(extracted_text)
    print(nippo.exportText())
    
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

    nippo.addTxt(backlogTxt)
    body += nippo.exportText()
    
    save_text_to_file(body,"../out/nippo_matome.txt")


if __name__ == "__main__":

    main()

# python3 nippo_end.py
