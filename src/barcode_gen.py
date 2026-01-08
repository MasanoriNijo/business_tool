import qrcode
import sys
import barcode
from barcode.writer import ImageWriter

# 生成するバーコードの種類を選択（例: Code128, EAN13, EAN8 など）
code_class = barcode.get_barcode_class('code128')

args = sys.argv
# barcode_data = args[1]
barcode_data = "13001 016100300025301 1"
img = code_class(barcode_data, writer=ImageWriter())
img.save('barcode')
# img.show()