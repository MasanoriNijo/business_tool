import json
import re
import sys
from file_text_module import out_put_object, read_file, join_array, save_text_to_file
import subprocess

ROOT_PATH = "C:/Users/masanori.nijo/Documents/chatGpt/src/mysql"

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
        # print("AAA")
        # print(work)
        if work["work"] == table_pos:
            return work
    return None

def refresh_work(works, works_org, all_clear = False):
    if all_clear:
        # echo コマンドを実行してファイルを空にする
        command2 = f'bash -c "echo \'\' > {ROOT_PATH}/file/work.txt"'
        subprocess.run(command2, shell=True, check=True)
    workTxt = ""
    for work in works:
        if not all_clear and work in works_org:
            continue
        # print(work)
        poss = work["work"].split("←")
        work_txt = f"work:{work['work']}\n"
        work_txt += f"table:{work['table']}\n"
        work_txt += f"cnt:{work['cnt']}\n"
        work_txt += f"mysql> {work['mysql']['query']}\n"
        work_txt += "+----------------------------+\n"
        work_txt += f"| {poss[-1]}_id |\n"
        work_txt += "+----------------------------+\n"
        for id in work['mysql']['result']:
            work_txt += f"| {id} |\n"
        work_txt += "+----------------------------+\n"
        work_txt += f"{len(work['mysql']['result'])} rows in set (x.xx sec)\n"
        workTxt += work_txt
    save_text_to_file(workTxt, f"{ROOT_PATH}/file/work.txt",False)

def add_comment_to_work(comment):
    save_text_to_file(comment,f"{ROOT_PATH}/file/work.txt",False)

def gen_referenced_table(target_table, tables, works, table_result, visited = [], referenced_tables = {}, poss = []):
    # print(target_table)
    # print(referenced_tables)
    # print(poss)
    if not referenced_tables:
        cnt_ = next(iter(tables[target_table].items()))
        # print('BBB')
        # print(cnt_)
        referenced_tables = [{target_table:[{"cnt":cnt_[1]["cnt"]},{"id":[]}]}]
        poss=[target_table]

    if target_table in visited:
        return referenced_tables
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
        work_['table'] = target_table
        work_['cnt'] = table_result[target_table]["cnt"]
        work_['mysql'] = {}
        query = f"select {target_table}_id from {target_table}"
        if parent_work == None:
            if check_column(target_table,"deleted_at",tables):
                query += f" where deleted_at is null order by updated_at desc limit 200;"
            else:
                query += f" order by updated_at desc limit 200;"
        else:
            parent_table = poss[-2]
            idsTxt = ""
            if parent_work["mysql"]["result"][0] == "ALL":
                if check_column(target_table,"deleted_at",tables):
                    query += f" where deleted_at is null order by updated_at desc limit 200;"
                else:
                    query += f" order by updated_at desc limit 200;"
            else:    
                for id in parent_work["mysql"]["result"]:
                    idsTxt += f"'{id}',"
                query += f" where {parent_table}_id in ({idsTxt[:-1]});"
        work_['mysql']['query'] = query
        if int(work_['cnt']) < 10000:            
            work_['mysql']['result'] = ["ALL"]         
            works.append(work_)
        else:
            same_work = find_work_from_query(query, works)
            if same_work:
                work_['mysql']['query'] = same_work['mysql']['query']      
                work_['mysql']['result'] = same_work['mysql']['result']       
                works.append(work_)
            else:
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
                _visited = visited.copy()                  
                result = gen_referenced_table(table, tables, works, table_result, _visited, referenced_tables, _poss)
                if result == None:
                    return None
                    
    return referenced_tables

# table構造データから、rootテーブルのリストを作成。rootテーブル:カラム内に外部主キーがないもの。
def check_root_tables(tables,table_result):
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
    for table in root_tables:
        table_result[table]["type"] = "root"        

    return root_tables

# table数の
def gen_table_result(tables):
    # テーブル名とID取得結果を保存するリストを初期生成する。
    table_result = {}
    
    for table, column in tables.items():
        table_result[table]={}
        table_result[table]["type"]="none"
        table_result[table]["id"]=[]

    # 正規表現パターン
    pattern = r"^\|(.*)\| (.*)\|$"

    # ファイルを読み込む
    with open(f"{ROOT_PATH}/file/table_cnt.txt", "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                table_name = match.group(1).strip() # テーブル名
                row_count = match.group(2).strip() # 行数
                if not table_name in table_result:
                    continue 
                table_result[table_name]["cnt"] = row_count
                if int(row_count) < 10000:
                    table_result[table_name]["sql"] = "ALL"
                else:
                    table_result[table_name]["sql"] = "PARTIAL"
                    
    return table_result

# table構造データから、rootテーブルのリストを作成。rootテーブル:カラム内に外部主キーがないもの。
def gen_table_ids(tables):
    table_ids = []
    for table, columns in tables.items():
        table_ids.append({table:[]})
    return table_ids

def read_work():
    workTxt = read_file(f"{ROOT_PATH}/file/work.txt")
    
    # パターン定義: 'work:' から次の 'work:' または文字列の終わりまで
    pattern = r'work:.*?(?=work:|$)'
    results = []
    
    # マッチ結果を取得
    matches = re.finditer(pattern, workTxt, re.DOTALL)
    # マッチした内容を表示
    for match in matches:
        # print(match.group())  # マッチした全体を取得
        # workとSQL部分を抽出する正規表現
        pattern = re.compile(r"work:(.*?)\ntable:(.*?)\ncnt:(.*?)\nmysql> (.*?)\n\+-+\+\n.*\n\+-+\+\n(.*?)\n\+-+\+", re.DOTALL)
        # 結果を格納するリスト
        # マッチ結果を処理
        for match in pattern.finditer(match.group()):
            work_label = match.group(1).strip()
            table_name = match.group(2).strip()
            table_cnt = match.group(3).strip()
            sql_query = match.group(4).strip()
            sql_result = match.group(5).strip().split("\n")
            # 各行の値をリストに格納        
            sql_result_list = [row.replace("|","").strip() for row in sql_result]
            
            # 結果を追加
            results.append({
                "work": work_label,
                "table": table_name,
                "cnt": table_cnt,
                "mysql": {
                    "query": sql_query,
                    "result": sql_result_list
                }
            })

    # JSON形式で保存
    output_file = "output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    # print(f"JSONファイルに出力しました: {output_file}")
    
    return results

def find_work_from_query(query, works):
    for work in works:
        if query == work["mysql"]["query"]:
            return work.copy()
    return None

def update_table_result_from_work(table_result, works):
    for work in works:
        table_result[work["table"]]["id"] += work["mysql"]["result"]
    
    # idの重複をする。
    for table, value in table_result.items():
        ids_ = list(set(value["id"]))
        value["id"].clear()
        value["id"] += ids_
        value["id_cnt"] = len(ids_)

def gen_dump_sql_from_table_result(table_result, last_command = "| gzip > ishigro_stg_orange_pos_@@@@.$(date +%Y%m%d)dump.gz"):
    allTablesTxt = ""
    whereTablesTxt = ""
    whereTxt = ""
    andTxt = ""
    for table, value in table_result.items():
        # print(table)
        # print(value)
        if value["sql"] == "ALL":
            allTablesTxt += f" {table}"
    last_command_ = last_command.replace("@@@@", "select_all_tables")
    result = f"{allTablesTxt} {last_command_}"

    Cnt = 0
    cnt_ = 0
    for table, value in table_result.items():
        # print(table)
        # print(value)
        if value["sql"] != "ALL":
            print(table)
            print(value)
            whereTablesTxt += f" {table}"
            whereTxt += f"{andTxt}{table}_id IN ('"
            whereTxt += "', '".join(value["id"])
            whereTxt += "') "
            andTxt = " AND "
            
            cnt_ += 1
            if cnt_ > Cnt:
                last_command_ = last_command.replace("@@@@", f"{table}_partial")
                result += f"\n{whereTablesTxt} --where=\"{whereTxt}\" {last_command_}"
                
                # 元に戻す
                cnt_ = 0
                whereTablesTxt = ""
                whereTxt = ""
                andTxt = ""
    # if whereTablesTxt:      
    #     result += f"\n{whereTablesTxt} --where=\"{whereTxt}\""

    return result            

def check_column(table_name, column, tables):
    if table_name in tables:
        table = tables[table_name]
        if column in table:
            return True
    return False

# 引数として検索したいキーを渡す関数
def get_dict_by_key(lst, key):
    for d in lst:
        if key in d:  # 辞書に指定のキーが含まれるか確認
            return d[key]
    return None  # 見つからない場合は None を返す

def main(target_table = "product"):
    
    out_path = f"{ROOT_PATH}/file/relate_tables"
    debug_path = f"{ROOT_PATH}/file/debug.txt"
    
    # JSONファイルを読み込む
    json_file = f"{ROOT_PATH}/file/tables.json"  # テーブル構造JSON
    tables = load_table_structure(json_file)
    table_result = gen_table_result(tables)
    check_root_tables(tables, table_result)
    out_put_object(table_result, debug_path)
    out_put_object(tables, debug_path)

    # print(root_tables)
    print(tables)
    # rootテーブルから処理する。
    add_comment_to_work("# rootテーブルから処理する。")
    for table, value in table_result.items():
        if value["type"] != "root":
            continue
        add_comment_to_work(f"# rootテーブル:{table}")
        print(table)
        # 任意のテーブルを指定してリレーションを探索
        works_org = read_work()
        works = works_org.copy()
        referenced_tables = gen_referenced_table(table, tables, works, table_result)
        refresh_work(works,works_org)
        if referenced_tables == None:
            sys.exit("プログラムを終了します")
        # echo コマンドを実行してファイルを空にする
        command2 = f'bash -c "echo \'\' > {out_path}_{table}.txt"'
        subprocess.run(command2, shell=True, check=True)
        out_put_object(referenced_tables, f"{out_path}_{table}.txt")
        
        
        # print(f"'{target_table}' が参照されるテーブル: {referenced_tables}")
        output_file = f"{ROOT_PATH}/file/relate_tables.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(referenced_tables, f, ensure_ascii=False, indent=4)       

    update_table_result_from_work(table_result, works)
    
    # ダンプ用文字列を生成
    command = f'bash -c "echo \'\' > {ROOT_PATH}/file/dump_where.txt"'
    subprocess.run(command, shell=True, check=True)
    dumpTxt = gen_dump_sql_from_table_result(table_result)
    save_text_to_file(dumpTxt,f"{ROOT_PATH}/file/dump_where.txt")
    
    # echo コマンドを実行してファイルを空にする
    command = f'bash -c "echo \'\' > {ROOT_PATH}/file/table_result.txt"'
    subprocess.run(command, shell=True, check=True)
    command = f'bash -c "echo \'\' > {ROOT_PATH}/file/works_result.txt"'
    subprocess.run(command, shell=True, check=True)
    out_put_object(table_result, f"{ROOT_PATH}/file/table_result.txt")
    out_put_object(works, f"{ROOT_PATH}/file/works_result.txt")
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()


# python3 gen_table_structure.py table_name

