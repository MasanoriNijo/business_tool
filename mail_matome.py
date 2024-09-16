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
        status, folders = mail.list()
        if status == "OK":
            for folder in folders:
                print(folder.decode())
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
    N = 4  # 例として直近7日間
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
                        return part.get_payload(decode=True).decode("utf-8")
                    except:
                        pass
    else:
        return msg.get_payload(decode=True).decode("utf-8")
    
    return ""


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
    
    # 4. 抽出されたテキストをAIでまとめる
    ai_summary = ai_summarize_texts(extracted_texts)
    
    print("AIによる要約されたテキスト: \n", ai_summary)

if __name__ == "__main__":
    # Gmailのユーザ名とアプリパスワード（Googleで2段階認証が有効の場合に必要）
    username = "masanori.nijo@s-cubism.jp"
    password = "11Me9900002"
    
    # 件名のフィルタリングキーワード（正規表現）
    keyword_regex = ".*勤怠連絡.*"
    
    # 実行
    main(username, password, keyword_regex)
