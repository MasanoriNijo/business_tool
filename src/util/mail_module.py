# config_reader.py
import json
import imaplib
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import email
from email.header import decode_header
import ssl
import re

import os
import pickle
import base64
import imaplib
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from util.config_reader import load_config
config = load_config("C:/Users/masanori.nijo/Documents/chatGpt/src/conf/config.json")

# 認証情報ファイル（ダウンロードした JSON のパス）url: https://console.cloud.google.com/auth/clients/854558543161-7cirncc5vnn5d2s6k7cidjahho1o3is9.apps.googleusercontent.com?inv=1&invt=AbqvkQ&project=resonant-rock-452210-b2
CLIENT_SECRET_FILE = config["CLIENT_SECRET_FILE"]
# スコープ（Gmail の IMAP アクセス）
SCOPES = config["SCOPES"]
EMAIL_ACCOUNT = config["EMAIL_ACCOUNT"]
GMAIL_CLIENT_ID = config["GMAIL_CLIENT_ID"]

# 現在のスクリプトのディレクトリを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# token.pickleを相対パスで指定
TOKEN_PATH = os.path.join(BASE_DIR, "../conf/token.pickle")

def get_oauth2_token():
    creds = None
    # 以前の認証情報を読み込む
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
            print(f"refresh_token:{creds.refresh_token}")

    # 認証情報がない場合は新規認証
    if not creds or not creds.valid:
        print("A")
        if creds and creds.expired and creds.refresh_token:
            print("B")
            creds.refresh(Request())
        else:
            print("C")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # トークンを保存
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
            
    print(f"refresh_token:{creds.refresh_token}")
    print("Access Token:", creds.token)
    return creds

def connect_to_gmail():
    try:
        creds = get_oauth2_token()
        # auth_string = "user={}\\1auth=Bearer {}\\1\\1".format(EMAIL_ACCOUNT, creds.token)
        auth_string = f"user={EMAIL_ACCOUNT}\x01auth=Bearer {creds.token}\x01\x01"
        print(auth_string)
        # auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        print(auth_string)
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        # mail.debug = 4  # デバッグ情報を表示
        mail.authenticate("XOAUTH2", lambda _: auth_string.encode("utf-8"))
        print("ログイン成功")
        return mail
    
    except imaplib.IMAP4.error as e:
        print(f"ログイン失敗: {e}")
        raise

    # 実行サンプル
    # mail = connect_to_gmail()
    # mail.select("INBOX")  # 受信トレイを選択

# メールサーバに接続
def connect_to_email_server(username, password, imap_server="imap.gmail.com", imap_port="993"):
    
    return connect_to_gmail()
    
    # 以下の認証ではログインできなくなったので、上に変更.
    # mail = imaplib.IMAP4_SSL(imap_server,imap_port)
    # print(username)
    # print(password)
    # try:
    #     mail.login(username, password)
    # except imaplib.IMAP4.error as e:
    #     print(f"ログイン失敗: {e}")
    #     raise
    
    # return mail

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

# 利用可能なメールフォルダー名を取得する
def list_folders(email_account, email_password, imap_server, imap_port):
    try:
        # SSLコンテキストを作成してIMAPサーバに接続
        context = ssl.create_default_context()
        with connect_to_gmail() as mail:
            # mail.login(email_account, email_password)
            
            # 利用可能なフォルダ（ラベル）を一覧表示
            result, folders = mail.list()
            if result == 'OK':
                print("利用可能なフォルダ一覧:")
                for folder in folders:
                    print(folder.decode())
            else:
                print("フォルダの一覧取得に失敗しました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        
# Gmailへ下書きを作成する。
def create_draft(email_account, password, subject, body, imap_server, imap_port):    
    # メールの作成
    msg = MIMEMultipart()
    msg['From'] = email_account
    msg['To'] = 'k@s-cubism.jp, d_system_support@s-cubism.jp'  # 宛先
    msg['Subject'] = subject

    # メール本文を追加
    msg.attach(MIMEText(body, 'plain'))

    # メールをIMAPサーバに送信
    try:
        # SSLコンテキストを作成してIMAPサーバに接続
        context = ssl.create_default_context()
        with connect_to_gmail() as mail:
            # mail.login(email_account, password)
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
