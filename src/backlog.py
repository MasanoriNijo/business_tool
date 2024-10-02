import requests
import sys
from datetime import datetime, timezone, timedelta
import subprocess
from util.backlog_module import fetch_backlog_tickets, fetch_backlog_comments, summarize_tickets

from util.config_reader import load_config
config = load_config()

# BacklogのAPI設定
API_KEY = config["BACKLOG_API_KEY"]
BACKLOG_SPACE = config["BACKLOG_SPACE"] 
PROJECT_DICT = config["PROJECT_DICT"] 

project_ids = []

# 要約をファイルに出力する関数
def save_summaries_to_file(summaries, output_file):
    with open(output_file, 'a', encoding='utf_8') as f:
        for ticket_key, summary in summaries.items():
            f.write(f"・{ticket_key} {summary['summary']}\n")
            f.write(f"  https://s-cubism.backlog.jp/view/{ticket_key}\n")
            for date, comment in summary['comments'].items():
                f.write(f"{' ' *3}→{date}:\n")
                f.write(f"{indent_text(remove_empty_lines(comment),4)}\n")
            f.write(f"\n")

# TXTをファイルに出力する関数
def save_text_to_file(txt, output_file):
    with open(output_file, 'a', encoding='utf_8') as f:
        f.write(f"{txt}\n")

# textを全行指定の文字数だけ字下げする。
def indent_text(text, indent_spaces):
    # 指定した文字数分のスペースを作成
    indent = ' ' * indent_spaces
    
    if not bool(text):
        return indent
    
    # 各行に字下げを適用
    indented_text = '\n'.join([indent + line for line in text.split('\n')])
    
    return indented_text

# 引数に指定されたテキストから空行やスペースのみの行を削除
def remove_empty_lines(text):
    if not bool(text):
        return ""
    # 各行について、空白文字だけの行や完全に空の行を除外して新しいリストを作成
    lines = text.splitlines()
    filtered_lines = [line for line in lines if line.strip()]
    
    # フィルタリング後の行を再度結合して返す
    return "\n".join(filtered_lines)

# 辞書のkey,valueを入れ替える
def invert_dict(input_dict):
    inverted_dict = {}

    # キーと値を入れ替え、重複する値はリストに追加
    for key, value in input_dict.items():
        # キーと値をutf_8でエンコードして扱う
        encoded_key = key.encode('utf_8')
        encoded_value = str(value).encode('utf_8')
        
        if encoded_value not in inverted_dict:
            inverted_dict[encoded_value] = []
        
        inverted_dict[encoded_value].append(encoded_key)
    
    # 辞書を昇順に並べ替え
    sorted_inverted_dict = {k.decode('utf_8'): [v.decode('utf_8') for v in inverted_dict[k]] for k in sorted(inverted_dict)}

    return sorted_inverted_dict

# メイン関数
def main(output_file="C:/Users/masanori.nijo/Documents/chatGpt/out/backlog_summary.txt", target_date=None, project_ids = []):
     
    # echo コマンドを実行してファイルを空にする
    command2 = ['bash', '-c', f"echo '' > {output_file}"]
    # コマンドの実行
    subprocess.run(command2, check=True)

    # 引数にproject_idsの指定の有無で場合分け
    if len(project_ids):
        for project_id in project_ids:
            # 1. 指定の日付
            tickets = fetch_backlog_tickets(date=target_date, project_id=project_id)
            
            if not tickets:
                print(f"project_id:{project_id} No tickets found for the specified date:{target_date}")
                continue

            # 2. チケットの要約を生成
            summaries = summarize_tickets(tickets, target_date)

            # 3. テキストファイルに出力
            save_summaries_to_file(summaries, output_file)
    
    else:
        projects = invert_dict(PROJECT_DICT)
        for name, projectIds in projects.items():
            save_text_to_file(f"▼{name}", output_file)
            for project_id in projectIds:
                # 1. 指定の日付
                tickets = fetch_backlog_tickets(date=target_date, project_id=project_id)               
                if not tickets:
                    print(f"{name}(project_id:{project_id}) No tickets found for the specified date:{target_date}")
                    continue

                # 2. チケットの要約を生成
                summaries = summarize_tickets(tickets, target_date)

                # 3. テキストファイルに出力
                save_summaries_to_file(summaries, output_file)
            save_text_to_file(f"", output_file)
        
    
    print(f"Summaries saved to {output_file}")

if __name__ == "__main__":

    # コマンドライン引数を取得（スクリプト名は sys.argv[0] に格納されるので省く）
    args = sys.argv[1:]

    # 引数の処理（例: 引数が key=value 形式で渡されたと仮定）
    variables = {}

    for arg in args:
        if "=" not in arg:
            if arg.isdigit():
                target_date_ = (datetime.now()-timedelta(days=int(arg))).strftime('%Y-%m-%d')
                variables['target_date'] = target_date_
            else:
                print("引数は、数字もしくは、project_ids=131529,131247,115673,55351 (target_date=2024-09-18 output_file=../out/backlog_summary.txt))の形式になります。")
                sys.exit()
        else:
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

 
    # print(project_ids)
    print(target_date)
    main(output_file=output_file, target_date=target_date, project_ids = project_ids)
    
# python3 backlog.py 3 3日前

# python3 backlog.py target_date=2024-09-18
# python3 backlog.py project_ids=131529,131247,115673,55351 (target_date=2024-09-18 output_file=../out/backlog_summary.txt)

# MANDC_UKETORI:131529
# MANDC_UKETORI_INNER:131247
# AEONPET_POS_CS:115673
# ISHIBASHI_ZENTAI:55351


