import qrcode
import sys

args = sys.argv
qr = args[1]
img = qrcode.make(qr)
img.save('qr.png')
img.show()