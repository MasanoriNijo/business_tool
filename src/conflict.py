import sys
from util.file_text_module import save_text_to_file
import subprocess

memo = {}  # 計算量削減のためのメモ化

def _conflict(ptn,n):
  """
  n個目が異なる確率
  """
  if n in memo:
    return memo[n]
  else:
    rate = (ptn-n)/ptn
    memo[n] = rate
    return rate

def conflict(ptn,n):
  """
  n個が全て異なる確率
  """
  rate = 1.0
  for i in range(1, n):
    rate *= _conflict(ptn,i)
  return rate


def not_conflict(ptn,n):
  """
  n個が少なくとも1組同じになる確率
  """
  return 1.0 - conflict(ptn,n)

def main(ptn = 100):
    
    command2 = ['bash', '-c', 'echo "n,rate" > C:/Users/masanori.nijo/Documents/chatGpt/out/conflict.csv']
    # コマンドの実行
    subprocess.run(command2, check=True)

    for n in range(2, ptn):
        rate = not_conflict(ptn,n)
        save_text_to_file(f"{n},{rate}","C:/Users/masanori.nijo/Documents/chatGpt/out/conflict.csv",False)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main()

# python3 conflict.py N Nはパターンの数
