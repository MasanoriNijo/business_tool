import imaplib
import ssl
from config_reader import load_config

config = load_config()

# GmailのIMAPサーバー情報
IMAP_SERVER = config["IMAP_SERVER"]
IMAP_PORT = config["IMAP_PORT"]
EMAIL_ACCOUNT = config["EMAIL_ACCOUNT"]  # 自分のGmailアドレス
PASSWORD = config["PASSWORD"]  # アプリパスワードを使用（通常のパスワードではなく、2段階認証のアプリパスワード）

def list_folders():
    try:
        # SSLコンテキストを作成してIMAPサーバに接続
        context = ssl.create_default_context()
        with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context) as mail:
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            
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

if __name__ == "__main__":
    list_folders()
