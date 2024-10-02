

# TXTをファイルに出力する関数
def save_text_to_file(txt, output_file):
    try:
        with open(output_file, 'a', encoding='utf_8') as f:
            f.write(f"{txt}\n")
        
    except IOError as e:
        print(f"An I/O error occurred: {e}")
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
