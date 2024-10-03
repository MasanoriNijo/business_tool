import sys
from util.file_text_module import read_file, save_text_to_file
import matplotlib.pyplot as plt

def showScatterGrapth(Xs,Ys):
    # 散布図を作成
    plt.scatter(Xs, Ys, color='blue', label='Sample Data')

    # グラフのタイトルとラベル
    plt.title('Sample Scatter Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    # 凡例を表示
    plt.legend()

    # グラフを表示
    plt.show()

def calc_tempo_recursive(waves, startInd=0, tempoWaves=[], pitch=0, pitchCnt=0):
    pithTole = 0.001 # ピッチの許容誤差
    waveTole = 0.1 # 波形値の許容減衰値
    matchPitchCnt = 5 # 判定OKとなるピッチ数
    
    if len(tempoWaves) == 0:
        while startInd < len(waves) and waves[startInd] <= 0.0:
            startInd +=1
        pitchCnt = 0
        tempoWaves.append({"ind":startInd,"value":waves[startInd]})
        return calc_tempo_recursive(waves,startInd,tempoWaves,pitch=0,pitchCnt=0)
    
    headWave = tempoWaves[-1]
    ind = int(headWave.ind + pitch*(1-pithTole))
    if ind > len(waves):
        return -1
    while ind < headWave.ind + pitch*(1+pithTole):
        if waves[ind] > headWave.val * (1-waveTole):
            if waves[ind] < headWave.val * (1+waveTole):
                pitch_add = ind - headWave.ind
                pitchCnt +=1
                pitch = (pitch * pitchCnt + pitch_add)/pitchCnt
                tempoWaves.append({"ind":ind,"value":waves[ind]})
                if pitchCnt == matchPitchCnt:
                    return [tempoWaves,pitch]
                return calc_tempo_recursive(waves,ind,tempoWaves,pitch,pitchCnt)
        ind += 1
    # ここに到達した場合は、再度0からtempoWaves[0].indの次からやり直し。
    startInd = tempoWaves[0].ind + 1
    calc_tempo_recursive(waves, startInd=startInd, tempoWaves=[], pitch=0, pitchCnt=0)
    
# メイン関数
def main(input_file=r"C:\Users\masanori.nijo\Documents\chatGpt\in\audioExtremeDataArray_sample.txt"):
    waveTxt = read_file(input_file)
    waveTexts =  waveTxt.replace('\n','').replace('\r','').split(',')
    waves =  [float(item) for item in waveTexts]
    xlines = [ind for ind in range(len(waves))]

    for wave in waves:
        save_text_to_file(txt=wave,output_file="../out/wave.txt",msg=False)
        
    showScatterGrapth(xlines,waves)

if __name__ == "__main__":

    # コマンドライン引数を取得（スクリプト名は sys.argv[0] に格納されるので省く）
    args = sys.argv[1:]
    input_file=r"C:\Users\masanori.nijo\Documents\chatGpt\in\audioExtremeDataArray_sample.txt"
    if len(args):
        input_file=args[0]
        
    main(input_file=input_file)
    
# python3 backlog.py 3 3日前

# python3 backlog.py target_date=2024-09-18
# python3 backlog.py project_ids=131529,131247,115673,55351 (target_date=2024-09-18 output_file=../out/backlog_summary.txt)



