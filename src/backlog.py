import requests
import sys
from datetime import datetime, timezone, timedelta
import subprocess

from config_reader import load_config
config = load_config("C:/Users/masanori.nijo/Documents/chatGpt/src/config.json")

# BacklogのAPI設定
API_KEY = config["BACKLOG_API_KEY"]
BACKLOG_SPACE = config["BACKLOG_SPACE"] 
PROJECT_KEY = config["PROJECT_KEY"] 
PROJECT_ID = config["PROJECT_ID"] 

project_ids = []

# チケットを取得する関数
def fetch_backlog_tickets(date=None, project_id=PROJECT_ID):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    url = f"https://{BACKLOG_SPACE}.backlog.jp/api/v2/issues"
    params = {
        'apiKey': API_KEY,
        'projectId[]': project_id,
        # 'createdSince': date,  # この日付以降に作成されたチケットを取得
        # 'createdUntil': date,  # この日付までに作成されたチケットを取得
        'updatedSince': date,  # この日付以降に更新されたチケットを取得
        # 'updatedUntil': date,  # この日付までに更新されたチケットを取得
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
        date = datetime.now().strftime('%Y-%m-%d')
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
def summarize_tickets(tickets, target_date):
    # summarizer = pipeline("summarization")
    summaries = {}
    
    for ticket in tickets:      
        # summary = summarizer(ticket_content, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        summaries[ticket['issueKey']]= {}
        summaries[ticket['issueKey']]["summary"] = ticket['summary']
        summaries[ticket['issueKey']]["comments"] = {}
        comments = fetch_backlog_comments(ticket['issueKey'])
        for comment in comments:
            updated_time = utc_to_jst(comment['updated'])
            if updated_time > f"{target_date} 00:00:00":
                summaries[ticket['issueKey']]["comments"][updated_time] = comment['content']
    
    return summaries

def utc_to_jst(utc_time_str):
    # 文字列からUTCの日時をパース
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    # UTCから日本時間(JST)に変換 (JSTはUTC+9時間)
    jst_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=9)))
    # 日本時間のフォーマットで出力
    return jst_time.strftime("%Y-%m-%d %H:%M:%S")

# 要約をファイルに出力する関数
def save_summaries_to_file(summaries, output_file):
    with open(output_file, 'a', encoding='utf-8') as f:
        for ticket_key, summary in summaries.items():
            f.write(f"・{ticket_key} {summary['summary']}\n")
            f.write(f"https://s-cubism.backlog.jp/view/{ticket_key}\n")
            for date, comment in summary['comments'].items():
                f.write(f" {date}:\n")
                f.write(f"  {comment}:\n")
                
# メイン関数
def main(output_file="C:/Users/masanori.nijo/Documents/chatGpt/out/backlog_summary.txt", target_date=None, project_ids = [PROJECT_ID]):
     
    # echo コマンドを実行してファイルを空にする
    command2 = ['bash', '-c', f"echo '' > {output_file}"]
    # コマンドの実行
    subprocess.run(command2, check=True)

    for project_id in project_ids:
        # 1. 指定の日付（または今日）でチケットを取得
        tickets = fetch_backlog_tickets(date=target_date, project_id=project_id)
        
        if not tickets:
            print(f"project_id:{project_id} No tickets found for the specified date:{target_date}")
            continue

        # 2. チケットの要約を生成
        summaries = summarize_tickets(tickets, target_date)

        # 3. テキストファイルに出力
        save_summaries_to_file(summaries, output_file)
    
    print(f"Summaries saved to {output_file}")

if __name__ == "__main__":

    # コマンドライン引数を取得（スクリプト名は sys.argv[0] に格納されるので省く）
    args = sys.argv[1:]

    # 引数の処理（例: 引数が key=value 形式で渡されたと仮定）
    variables = {}
    for arg in args:
        key, value = arg.split('=')
        variables[key] = value
   
    if "target_date" in variables.keys():
        target_date = variables["target_date"]
    else:
        target_date = datetime.now().strftime('%Y-%m-%d') 
        
    if "output_file" in variables.keys():
        output_file = variables["output_file"]
    else:
        output_file = "C:/Users/masanori.nijo/Documents/chatGpt/out/backlog_summary.txt"
        
    if "project_ids" in variables.keys():
        project_ids = variables["project_ids"].split(',')
    else:
        project_ids = [PROJECT_ID]
 
    # print(project_ids)
    print(target_date)
    main(output_file=output_file, target_date=target_date, project_ids = project_ids)
    
# python3 backlog.py project_ids=131529,131247,115673,55351 (target_date=2024-09-18 output_file=../out/backlog_summary.txt)

# MANDC_UKETORI:131529
# MANDC_UKETORI_INNER:131247
# AEONPET_POS_CS:115673
# ISHIBASHI_ZENTAI:55351


