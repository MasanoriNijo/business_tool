import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import ssl
import pytz

# GmailのIMAPサーバー情報
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "masanori.nijo@s-cubism.jp"  # 自分のGmailアドレス
PASSWORD = "11Me9900002"  # アプリパスワードを使用（通常のパスワードではなく、2段階認証のアプリパスワード）

def create_draft(subject, body):
    """Gmailに下書きを作成する関数"""
    
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
    # 現在の日付時刻を取得して件名と本文に反映
    now = datetime.now()
    current_date = now.strftime(f"%Y/%m/%d {get_japanese_weekday(now)}")
    current_time = now.strftime("%H:%M")
    subject = f"【勤怠連絡】{current_date} 二條 リモート"
    body = f"\n本日の業務を開始します。\n\n開始 {current_time} -"
    
    create_draft(subject, body)

if __name__ == "__main__":
    main()
