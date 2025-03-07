from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import re
from util.config_reader import load_config
from util.mail_module import connect_to_email_server, filter_emails_by_subject, extract_text_from_email, create_draft

config = load_config("C:/Users/masanori.nijo/Documents/chatGpt/src/conf/config.json")

# GmailのIMAPサーバー情報
IMAP_SERVER = config["IMAP_SERVER"]
IMAP_PORT = config["IMAP_PORT"]
EMAIL_ACCOUNT = config["EMAIL_ACCOUNT"]  # 自分のGmailアドレス
PASSWORD = config["PASSWORD"]  # 自分のGmailのパスワード
APLI_PASSWORD = config["APLI_PASSWORD"]  # アプリパスワードを使用（通常のパスワードではなく、2段階認証のアプリパスワード）

remoteFlg = True  # リモート勤務の場合True

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
    # 現在の日付時刻を取得して件名と本文に反映
    now = datetime.now()
    current_date = now.strftime(f"%Y/%m/%d {get_japanese_weekday(now)}")
    current_time = now.strftime("%H:%M")
    subject = f"【勤怠連絡】{current_date} 二條 {'リモート' if remoteFlg else '出社'}"

    keyword_regex = "^Re: 【勤怠連絡】\d{4}/\d{1,2}/\d{1,2} [日月火水木金土] 二條 (リモート|出社)$"
    mail = connect_to_email_server(EMAIL_ACCOUNT, APLI_PASSWORD)
    filtered_emails = filter_emails_by_subject(mail, 14, folder = "[Gmail]/&kAFP4W4IMH8w4TD8MOs-", keyword_regex = keyword_regex)
    subjects = filtered_emails[1]
    print(subjects)
    if len(filtered_emails[0]):
        extracted_text = extract_text_from_email(filtered_emails[0][-1])
        
        # 2024年9月12日(木) 10:43 二條正則 <masanori.nijo@s-cubism.jp>: のところを含むそれ以降は削除。
        ignore_ptn = r"(.*?)(?=\d{4}年\d{1,2}月\d{1,2}日\([月火水木金土日]\) \d{1,2}:\d{2} .*? <.*?>)"
        match = re.search(ignore_ptn, extracted_text, re.DOTALL)    
        if match:
            extracted_text = match.group(1).strip() + "END@@@"
        
        pattern = r'▼[\s\S]*?(?=▼|END@@@)'

        matchs = re.findall(pattern, extracted_text)
        extracted_text = ''
        if matchs:
            for match in matchs:
                extracted_text += f"{match}" 
        
        # 文字の前後の空白改行コードを削除する
        extracted_text = extracted_text.strip()
        extracted_text = extracted_text.strip("\n")
        extracted_text = extracted_text.strip("\r")
        
        print(extracted_text)
    body = f"\n本日の業務を開始します。\n\n開始:{current_time} -\n\n{extracted_text}\n\n▼その他\n・チケット発生都度対応"
    create_draft(EMAIL_ACCOUNT, subject, body)

if __name__ == "__main__":
    if len(sys.argv) > 1:
    # 最初の要素はスクリプト名なので、それ以降を取得
        if sys.argv[1] == "s":
            remoteFlg = False
    main()

# python3 nippo_start.py s // 出社の場合は引数にsを追記
