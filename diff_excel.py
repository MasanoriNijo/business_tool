import pandas as pd
import sys

# コマンドライン引数を確認
if len(sys.argv) != 3:
    print("使い方: python3 compare_excel.py file1.xlsx file2.xlsx")
    sys.exit(1)

# 2つのExcelファイルをコマンドライン引数から取得
file1 = sys.argv[1]
file2 = sys.argv[2]

# Excelファイルを読み込む
try:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
except Exception as e:
    print(f"エクセルファイルの読み込みエラー: {e}")
    sys.exit(1)

# 差分を確認する
comparison_result = df1.compare(df2)

# 差分をテキストファイルに出力
output_file = "excel_diff.txt"
with open(output_file, "w") as f:
    if comparison_result.empty:
        f.write("両ファイルに差分はありません。\n")
    else:
        f.write("両ファイルの差分:\n")
        f.write(comparison_result.to_string())

print(f"差分は {output_file} に出力されました。")
