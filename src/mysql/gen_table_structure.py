import re
import json
import sys

def parse_mysqldump(filename):
    # 結果を保存する辞書
    tables = {}

    # CREATE TABLE 文を検出する正規表現
    create_table_pattern = re.compile(r'CREATE TABLE `(?P<name>\w+)` \((?P<definition>.*?)\) ENGINE=', re.DOTALL)

    # ファイルを読み込む
    with open(filename, 'r', encoding='utf-8') as f:
        dump_content = f.read()

    # CREATE TABLE 文を抽出
    matches = create_table_pattern.finditer(dump_content)
    for match in matches:
        table_name = match.group('name')  # テーブル名
        table_definition = match.group('definition')  # テーブル定義

        # 各列情報を抽出する正規表現
        columns = []
        for line in table_definition.splitlines():
            line = line.strip().rstrip(',')
            # カラム定義を検出
            column_match = re.match(r'`(?P<name>\w+)` (?P<type>.+)', line)
            if column_match:
                columns.append({
                    "column_name": column_match.group('name'),
                    "column_type": column_match.group('type')
                })
        
        # 結果を辞書に追加
        tables[table_name] = columns

    return tables


# MySQLダンプファイルをJSONに変換して保存
def dump_to_json(input_file, output_file):
    tables = parse_mysqldump(input_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tables, f, indent=4, ensure_ascii=False)

    print(f"JSONファイルに変換完了: {output_file}")

def main(input_dump = '../../in/ishiguro_orange_pos_structure.dump', output_json = "../../out/tables.json"):
    dump_to_json(input_dump, output_json)
    

# 使用例
if __name__ == "__main__":
        if len(sys.argv) > 1:
            main(sys.argv[1])
        else:
            main()


# python3 gen_table_structure.py path/to/dump_file