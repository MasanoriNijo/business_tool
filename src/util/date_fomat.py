import re

def extract_times(input_file, output_file):
    # 正規表現パターンを定義 ([YYYY-MM-DD HH:MM:SS] の形式にマッチ)
    time_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'

    # 時間リストを作成
    times = []

    # 入力ファイルを開いて読み込む
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            # 正規表現で時間部分をすべて抽出
            matches = re.findall(time_pattern, line)
            times.extend(matches)

    # 結果を出力ファイルに書き込む
    with open(output_file, 'w', encoding='utf-8') as output:
        for time in times:
            output.write(time + '\n')

# 使用例
input_file = '../in/input.txt'   # 入力ファイル名
output_file = '../out/output.txt' # 出力ファイル名
extract_times(input_file, output_file)

print(f"抽出した時間は {output_file} に保存されました。")
