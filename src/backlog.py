import requests
import sys
import datetime
from transformers import pipeline

# BacklogのAPI設定
API_KEY = "GXNC3ZmSXMWUQ5fDGvAe0xszjAMA21JqNuEkUkyCN9bHsxy0DLxBR0yFbW5MgUAd"
BACKLOG_SPACE = "s-cubism"  # 例: 'yourteam'
PROJECT_KEY = "MANDC_UKETORI"  # 例: 'PRJ'

# チケットを取得する関数
def fetch_backlog_tickets(date=None):
    if date is None:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
    date = "2024-09-17"
    url = f"https://{BACKLOG_SPACE}.backlog.jp/api/v2/issues"
    params = {
        'apiKey': API_KEY,
        'projectId[]': 131529,
        # 'createdSince': date,  # この日付以降に作成されたチケットを取得
        # 'createdUntil': date,  # この日付までに作成されたチケットを取得
        'updatedSince': date,  # この日付以降に作成されたチケットを取得
        # 'updatedUntil': date,  # この日付までに作成されたチケットを取得
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching tickets: {response.status_code}, {response.text}")
        sys.exit(1)
        
# チケットのコメントを取得する関数
def fetch_backlog_comments(ticketCode, date=None):
    if date is None:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
    date = "2024-09-17"
    url = f"https://{BACKLOG_SPACE}.backlog.jp/api/v2/issues/{ticketCode}/comments"
    params = {
        'apiKey': API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching tickets: {response.status_code}, {response.text}")
        sys.exit(1)

# チケットの要約を生成する関数
def summarize_tickets(tickets):
    # summarizer = pipeline("summarization")
    summaries = []
    
    for ticket in tickets:
        
        comments = fetch_backlog_comments(ticket['issueKey'])
        ticket_content = ticket['summary'] + " " + ticket.get('description', "")
        # summary = summarizer(ticket_content, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append((ticket['issueKey'], ticket_content))
    
    return summaries

# 要約をファイルに出力する関数
def save_summaries_to_file(summaries, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for ticket_key, summary in summaries:
            f.write(f"Ticket: {ticket_key}\n")
            f.write(f"Summary: {summary}\n")
            f.write("="*40 + "\n")

# メイン関数
def main(output_file="backlog_summary.txt", target_date=None):
    # 1. 指定の日付（または今日）でチケットを取得
    tickets = fetch_backlog_tickets(date=target_date)
    
    if not tickets:
        print("No tickets found for the specified date.")
        return

    # 2. チケットの要約を生成
    summaries = summarize_tickets(tickets)

    # 3. テキストファイルに出力
    save_summaries_to_file(summaries, output_file)
    print(f"Summaries saved to {output_file}")

if __name__ == "__main__":
    # コマンドライン引数で出力ファイルと日付を指定可能
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "backlog_summary.txt"
    
    if len(sys.argv) > 2:
        target_date = sys.argv[2]
    else:
        target_date = None  # Noneの場合は今日の日付

    main(output_file=output_file, target_date=target_date)
