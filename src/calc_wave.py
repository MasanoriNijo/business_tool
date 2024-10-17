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
    pithTole = 0.05 # ピッチの許容誤差
    waveTole = 0.3 # 波形値の許容減衰値
    matchPitchCnt = 5 # 判定OKとなるピッチ数
    
    if len(tempoWaves) < 2:
        while startInd < len(waves) and waves[startInd] <= 0.0:
            startInd +=1
        if startInd == len(waves):
            print(f"NG！A")
            return -1
            
        if len(tempoWaves)==0:
            tempoWaves.append({"ind":startInd,"val":waves[startInd]})
            pitch=0
            pitchCnt=0
            startInd +=1
            return calc_tempo_recursive(waves,startInd,tempoWaves,pitch,pitchCnt)
        elif len(tempoWaves)==1:
            if waves[startInd] > tempoWaves[0]['val'] * (1-waveTole):
                if waves[startInd] < tempoWaves[0]['val'] * (1+waveTole):
                    tempoWaves.append({"ind":startInd,"val":waves[startInd]})                   
                    pitch = tempoWaves[1]['ind']-tempoWaves[0]['ind']            
                    pitchCnt=1
                    startInd +=1
                    return calc_tempo_recursive(waves,startInd,tempoWaves,pitch,pitchCnt)
        startInd +=1
        return calc_tempo_recursive(waves,startInd,tempoWaves,pitch,pitchCnt)

    headWave = tempoWaves[-1]
    ind = int(headWave['ind'] + pitch*(1-pithTole))
    if ind > len(waves):
        print(f"NG！B")
        return -1
    while ind < headWave['ind'] + pitch*(1+pithTole):
        if waves[ind] > headWave['val'] * (1-waveTole):
            if waves[ind] < headWave['val'] * (1+waveTole):
                pitch_add = ind - headWave['ind']
                pitch = (pitch * pitchCnt + pitch_add)/(pitchCnt+1)
                pitchCnt +=1
                tempoWaves.append({"ind":ind,"val":waves[ind]})
                if pitchCnt == matchPitchCnt:
                    return [pitch,tempoWaves]
                return calc_tempo_recursive(waves,ind,tempoWaves,pitch,pitchCnt)
            else:
                print(f"ind:{ind},value:{waves[ind]}")
                print([pitch,tempoWaves])
        elif waves[ind]>0:
            print(f"ind:{ind},value:{waves[ind]}")
            print([pitch,tempoWaves])
                
        ind += 1
        
    # ここに到達した場合は、再度0からtempoWaves[0].indの次からやり直し。
    print(f"ind:{ind},value:{waves[ind]}")
    print([pitch,tempoWaves])
    startInd = tempoWaves[0]['ind'] + 1
    return calc_tempo_recursive(waves, startInd=startInd, tempoWaves=[], pitch=0, pitchCnt=0)
    
# メイン関数
def main(input_file=r"C:\Users\masanori.nijo\Documents\chatGpt\in\audioExtremeDataArray_sample.txt"):
    waveTxt = read_file(input_file)
    waveTexts =  waveTxt.replace('\n','').replace('\r','').split(',')
    waves =  [float(item) for item in waveTexts]
    xlines = [ind for ind in range(len(waves))]

    ind = 0
    for wave in waves:
        if wave != 0.0:
            save_text_to_file(txt=f"{ind},{wave}",output_file="../out/wave.txt",msg=False)
        ind +=1
    answer = calc_tempo_recursive(waves=waves)
    print("anser")
    print(answer)
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



