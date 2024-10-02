import imaplib
import ssl
from util.config_reader import load_config
from util.mail_module import list_folders

config = load_config()

# GmailのIMAPサーバー情報
IMAP_SERVER = config["IMAP_SERVER"]
IMAP_PORT = config["IMAP_PORT"]
EMAIL_ACCOUNT = config["EMAIL_ACCOUNT"]  # 自分のGmailアドレス
PASSWORD = config["PASSWORD"]  # アプリパスワードを使用（通常のパスワードではなく、2段階認証のアプリパスワード）

if __name__ == "__main__":
    list_folders(EMAIL_ACCOUNT,PASSWORD,IMAP_SERVER,IMAP_PORT)
