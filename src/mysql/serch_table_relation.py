import json
import re
import sys
from file_text_module import out_put_object
import subprocess

def load_table_structure(json_file):
    """JSONからテーブル構造を読み込む"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_foreign_keys(tables):
    """各テーブルの外部キー情報を解析してリレーションを構築"""
    relations = {}
    id_pattern = re.compile('(^.*)_id$')
    
    for table, columns in tables.items():
        relations[table] = []
        for column in columns:
            column_name = column["column_name"]
            match = re.match(id_pattern,column_name)
            if match:
                relations[table].append(match[1])
    
    return relations

def new_func():
    return []


def find_referenced_table(target_table, tables, visited = [], referenced_tables = {}, poss = []):
    # print(target_table)
    # print(referenced_tables)
    # print(poss)
    if not referenced_tables:
        referenced_tables = [{target_table:[]}]
        poss=[target_table]

    if target_table in visited:
        return
    visited.append(target_table)
    
    for table, columns in tables.items():
        if table == target_table:
            continue

        for column, value in columns.items():
            if column == target_table + "_id":
                ref = referenced_tables
                n=0           
                for pos in poss:
                    # print(n)
                    # print(pos)
                    # print(ref)
                    ref = get_dict_by_key(ref,pos)
                    # print(ref)
                    n+=1
                print(value)
                key = table
                ref.append({key:[{"cnt":value["cnt"]}]})
                _poss = poss.copy()
                _poss.append(table)                    
                find_referenced_table(table,tables,visited,referenced_tables, _poss)
                    
    return referenced_tables

# 引数として検索したいキーを渡す関数
def get_dict_by_key(lst, key):
    for d in lst:
        if key in d:  # 辞書に指定のキーが含まれるか確認
            return d[key]
    return None  # 見つからない場合は None を返す

def main(target_table = "product"):
    
    out_path = "C:/Users/masanori.nijo/Documents/chatGpt/out/relate_tables.txt"
    # echo コマンドを実行してファイルを空にする
    command2 = f'bash -c "echo \'\' > {out_path}"'
    subprocess.run(command2, shell=True, check=True)
    
    # JSONファイルを読み込む
    json_file = "C:/Users/masanori.nijo/Documents/chatGpt/out/tables.json"  # テーブル構造JSON
    tables = load_table_structure(json_file)
    # print(tables)

    # 任意のテーブルを指定してリレーションを探索
    referenced_tables = find_referenced_table(target_table, tables)

    # print(f"'{target_table}' が参照されるテーブル: {referenced_tables}")
    output_file = "C:/Users/masanori.nijo/Documents/chatGpt/out/relate_tables.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(referenced_tables, f, ensure_ascii=False, indent=4)
        
    out_put_object(referenced_tables, out_path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()


# python3 gen_table_structure.py table_name

