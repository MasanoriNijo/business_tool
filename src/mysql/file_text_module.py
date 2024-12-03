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
    # 各行を処理して、結果をリストにまとめる
    lines = [line.strip() for line in txt.split("\r\n") if line.strip()]
    # 再びテキストとして結合
    return "\r\n".join(lines)

# 配列の集合体を字下げでtext出力
def out_put_object(obj, file, lvl = 0):
    if isinstance(obj,list):
        for value in obj:
            out_put_object(value,file,lvl+1)            
    elif isinstance(obj,dict):
        for key, value in obj.items():
            if isinstance(value,list) or isinstance(value,dict):     
                save_text_to_file(" " * lvl + key, file,False)
                out_put_object(value,file,lvl+1)
            else:        
                save_text_to_file(" " * lvl + key + ": " + value, file,False)
    else:
        save_text_to_file("  " * lvl + obj,file,False)

# xxx,yyyの2項形式のCSV(ヘッダ無し)をkey:xxx,value:yyyに辞書化する。
def gen_dict_from_csv(file_path):
    dict = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file):
            # ヘッダー行をスキップ
            # if line_number == 0:
            #     continue
            # 行をカンマで分割してキーと値を取得
            key, value = line.strip().split(",")
            # 辞書に追加（値を整数に変換）
            dict[key] = value
    return dict

# 配列を指定の結合文字で結合し、空要素を除外する関数。
def join_array(elements, separator):
    # 空要素を除外して結合
    return separator.join(str(element) for element in elements if element)