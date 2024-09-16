import os
import shutil

# 現在の作業ディレクトリを取得
current_directory = os.getcwd()

# 実行しているプログラムのファイル名を取得
# 実行ファイル自体の拡張子は、EXEや他の形式を想定
executable_file = os.path.basename(__file__)  # 実行ファイルの名前（例：script.pyやscript.exe）

# ディレクトリ内のファイル一覧を取得
files_in_directory = [f for f in os.listdir(current_directory) if os.path.isfile(os.path.join(current_directory, f))]

# ファイルを種類ごとにフォルダに移動
for file in files_in_directory:
    # 実行ファイルは処理対象外にする
    if file == executable_file:
        print(f"{file} は実行ファイルのため、処理をスキップします。")
        continue
    
    # ファイルの拡張子を取得
    file_extension = os.path.splitext(file)[1][1:].lower()  # 拡張子のピリオドを除去し、小文字に統一

    if file_extension:  # 拡張子が存在するファイルのみ処理
        folder_name = os.path.join(current_directory, file_extension)  # 種類ごとのフォルダ名
        file_path = os.path.join(current_directory, file)  # ファイルのフルパス
        
        # フォルダが存在しない場合は作成
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # ファイルを種類ごとのフォルダに移動
        shutil.move(file_path, os.path.join(folder_name, file))
        print(f"{file} を {folder_name} に移動しました。")
    else:
        print(f"{file} は拡張子がないため、処理をスキップしました。")
