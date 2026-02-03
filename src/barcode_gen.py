import qrcode
import sys
import barcode
from barcode.writer import ImageWriter

# if len(sys.argv) < 2:
#     print("使い方: python barcode.py <barcode_data>")
#     sys.exit(1)

# 生成するバーコードの種類を選択（例: Code128, EAN13, EAN8 など）
# code_class = barcode.get_barcode_class('code128')
code_class = barcode.get_barcode_class('code39')

barcode_data = "SAMPLE1234"

args = sys.argv
if len(sys.argv) > 1:
    barcode_data = args[1].upper()

img = code_class(barcode_data, writer=ImageWriter())

imgFilePath = '../out/bar_code/code_' + barcode_data
img.save(imgFilePath)
print(imgFilePath + '.png')

# 実行コマンド
# python3 barcode_gen.py HOGEHOGE

