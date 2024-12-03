import json
import re
import sys
from file_text_module import out_put_object, read_file, join_array, save_text_to_file
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

def find_work(table_pos,works):
    for work in works:
        print("AAA")
        print(work)
        if work["work"] == table_pos:
            return work
    return None

def refresh_work(works):
    # echo コマンドを実行してファイルを空にする
    command2 = f'bash -c "echo \'\' > C:/Users/masanori.nijo/Documents/chatGpt/src/mysql/file/work.txt"'
    subprocess.run(command2, shell=True, check=True)
    workTxt = ""
    for work in works:
        # print(work)
        poss = work["work"].split("←")
        work_txt = f"work:{work['work']}\n"
        work_txt += f"mysql> {work['mysql']['query']}\n"
        work_txt += "+----------------------------+\n"
        work_txt += f"| {poss[-1]}_id |\n"
        work_txt += "+----------------------------+\n"
        for id in work['mysql']['result']:
            work_txt += f"| {id} |\n"
        work_txt += "+----------------------------+\n"
        work_txt += f"{len(work['mysql']['result'])} rows in set (x.xx sec)\n"
        workTxt += work_txt
    save_text_to_file(workTxt,"C:/Users/masanori.nijo/Documents/chatGpt/src/mysql/file/work.txt")

def gen_referenced_table(target_table, tables, works, visited = [], referenced_tables = {}, poss = []):
    # print(target_table)
    # print(referenced_tables)
    # print(poss)
    if not referenced_tables:
        cnt_ = next(iter(tables[target_table].items()))
        print('BBB')
        print(cnt_)
        referenced_tables = [{target_table:[{"cnt":cnt_[1]["cnt"]},{"id":[]}]}]
        poss=[target_table]

    if target_table in visited:
        return
    visited.append(target_table)
    table_pos = join_array(poss,"←")
    work = find_work(table_pos,works)
    if work == None:
        parent_work = None
        if len(poss)>1:
            parent_table_pos = join_array(poss[:-1],"←")
            parent_work = find_work(parent_table_pos, works)
        
        work_ = {}
        work_['work'] = table_pos
        work_['mysql'] = {}
        query = f"select {target_table}_id from {target_table} "
        if parent_work == None:
            query += f" where deleted_at is null order by updated_at desc limit 10000"
        else:
            parent_table = poss[:-2]
            idsTxt = ""
            for id in parent_work["mysql"]["result"]:
                idsTxt += f"'{id}',"
            query += f" where {parent_table}_id in ({idsTxt[:-1]})"
        work_['mysql']['query'] = query        
        work_['mysql']['result'] = ["TODO"]         
        works.append(work_)
        print("以下処理してください")
        print(work_)
        return None
    
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
                # print(value)
                key = table
                ref.append({key:[{"cnt":value["cnt"]},{"id":[]}]})
                _poss = poss.copy()
                _poss.append(table)                    
                gen_referenced_table(table,tables,works,visited,referenced_tables, _poss)
                    
    return referenced_tables

# table構造データから、rootテーブルのリストを作成。rootテーブル:カラム内に外部主キーがないもの。
def find_root_tables(tables):
    root_tables = []
    for table, columns in tables.items():
        findRoot = True
        for column, value in columns.items():
            rootPtn = "(^.*)_id$"
            match = re.match(rootPtn,column)
            if match and match[1] != table:
                findRoot = False
                break
        if findRoot:
            root_tables.append(table)
    return root_tables

# table構造データから、rootテーブルのリストを作成。rootテーブル:カラム内に外部主キーがないもの。
def gen_table_ids(tables):
    table_ids = []
    for table, columns in tables.items():
        table_ids.append({table:[]})
    return table_ids

def read_work():
    workTxt = read_file("C:/Users/masanori.nijo/Documents/chatGpt/src/mysql/file/work.txt")
    
    # パターン定義: 'work:' から次の 'work:' または文字列の終わりまで
    pattern = r'work:.*?(?=work:|$)'
    results = []
    
    # マッチ結果を取得
    matches = re.finditer(pattern, workTxt, re.DOTALL)
    # マッチした内容を表示
    for match in matches:
        print(match.group())  # マッチした全体を取得
        # workとSQL部分を抽出する正規表現
        pattern = re.compile(r"work:(.*?)\nmysql> (.*?)\n\+-+\+\n.*\n\+-+\+\n(.*?)\n\+-+\+", re.DOTALL)
        # 結果を格納するリスト
        # マッチ結果を処理
        for match in pattern.finditer(match.group()):
            work_label = match.group(1).strip()
            sql_query = match.group(2).strip()
            sql_result = match.group(3).strip().split("\n")
            # 各行の値をリストに格納        
            sql_result_list = [row.replace("|","").strip() for row in sql_result]
            
            # 結果を追加
            results.append({
                "work": work_label,
                "mysql": {
                    "query": sql_query,
                    "result": sql_result_list
                }
            })

    # JSON形式で保存
    output_file = "output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"JSONファイルに出力しました: {output_file}")
    
    return results


# 引数として検索したいキーを渡す関数
def get_dict_by_key(lst, key):
    for d in lst:
        if key in d:  # 辞書に指定のキーが含まれるか確認
            return d[key]
    return None  # 見つからない場合は None を返す

def main(target_table = "product"):
    
    out_path = "C:/Users/masanori.nijo/Documents/chatGpt/src/mysql/file/relate_tables.txt"

    # echo コマンドを実行してファイルを空にする
    command2 = f'bash -c "echo \'\' > {out_path}"'
    subprocess.run(command2, shell=True, check=True)
    
    # JSONファイルを読み込む
    json_file = "C:/Users/masanori.nijo/Documents/chatGpt/src/mysql/file/tables.json"  # テーブル構造JSON
    tables = load_table_structure(json_file)
    table_ids = gen_table_ids(tables)
    
    root_tables = find_root_tables(tables)
    # print(root_tables)
    # print(tables)
    for target_table in root_tables:
        # 任意のテーブルを指定してリレーションを探索
        works = read_work()
        referenced_tables = gen_referenced_table(target_table, tables, works)
        refresh_work(works)
        if referenced_tables == None:
            sys.exit("プログラムを終了します")

        # print(f"'{target_table}' が参照されるテーブル: {referenced_tables}")
        output_file = "C:/Users/masanori.nijo/Documents/chatGpt/src/mysql/file/relate_tables.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(referenced_tables, f, ensure_ascii=False, indent=4)       
        out_put_object(referenced_tables, out_path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()


# python3 gen_table_structure.py table_name

