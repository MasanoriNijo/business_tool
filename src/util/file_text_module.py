import os

# TXTをファイルに出力する関数
def save_text_to_file(txt, output_file, msg=True):
    try:
        with open(output_file, 'a', encoding='utf_8') as f:
            f.write(f"{txt}\n")
        
    except IOError as e:
        print(f"An I/O error occurred: {e}")
    if msg:
        print(f"書き込み完了:path {output_file}")

# テキスト記入
def append_text_to_file(text, filename):
    try:
        # 'a' モードでファイルを開く（ファイルがなければ作成される）
        with open(filename, 'a') as file:
            file.write(text + '\n')  # 指定されたテキストを追記
        # print(f"'{text}' has been appended to {filename}.")
    except IOError as e:
        # 入出力エラーをキャッチ
        print(f"An I/O error occurred: {e}")

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

# 引数に指定したファイルの情報を読み込む
def read_file(file_path):
    try:
        # 指定されたファイルを読み込む
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: {file_path} が見つかりません。")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_files_with_extension(folder_path, extension = 'xlsx'):

    file_list = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(extension):
                file_list.append(os.path.join(root, file))
    
    return file_list

# 余分な改行、空白を削除する
def trim_text_all(txt):
    out_put = ''
    for item in txt.split("\n"):
        item = item.strip()
        item = item.strip("\n")
        item = item.strip("\r")
        item = item.strip("\n")
        item = item.strip("\r")
        item = item.strip()
        item = item.replace('\r','')
        item = item.replace('\n','')
        if item:
            out_put += item + '\r\n' 
    return out_put