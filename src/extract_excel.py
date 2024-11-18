import sys
import subprocess
from util.excel_module import excel_to_text
from util.file_text_module import save_text_to_file, get_files_with_extension, trim_text_all
from util.config_reader import load_config


config = load_config("C:/Users/masanori.nijo/Documents/chatGpt/src/conf/config.json")

EXCELL_ALL_FILE = config["EXCELL_ALL_FILE"]

def main(folder_path = 'C:/Users\masanori.nijo/Documents/chatGpt/in'):

    command2 = ['bash', '-c', 'echo "" > C:/Users/masanori.nijo/Documents/chatGpt/out/excel_all.txt']
    # コマンドの実行
    subprocess.run(command2, check=True)

    file_paths = get_files_with_extension(folder_path)
    
    for file_path in file_paths:
        try:
            print(file_path)
            save_text_to_file( "WORKBOOK:" + file_path + "\r\n" , 'C:/Users/masanori.nijo/Documents/chatGpt/out/excel_all.txt')
            result = excel_to_text(file_path)
            result = trim_text_all(result)
            save_text_to_file(result, 'C:/Users/masanori.nijo/Documents/chatGpt/out/excel_all.txt')
        except Exception as e:
            print(e)
        finally:
            continue

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

# python3 extract_excel.py path/to/folder