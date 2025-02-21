import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import sys

# コマンドライン引数をパースして辞書に格納
def parse_arguments(args):
    arg_dict = {}
    for arg in args:
        if ":" in arg:
            key, value = arg.split(":", 1)  # コロンで分割（1回だけ）
            arg_dict[key] = value
    return arg_dict

def movePolygon(polygon,x,y):
    newXY=[]
    for xy in polygon.get_xy():
        newXY.append([xy[0]+x,xy[1]+y])
    polygon.set_xy(newXY)

def moveC(light,dt,v,vc):
    x_data, y_data = light.get_data()
    x = x_data[0]
    y = y_data[0]
    # 方向ベクトルの正規化（単位ベクトル化）
    norm = np.linalg.norm(vc)
    if norm == 0:
        raise ValueError("方向ベクトル vc がゼロベクトルです。")
    
    unit_vc = vc / norm  # 正規化

    # 速度ベクトルを計算
    displacement = unit_vc * v * dt

    # 新しい位置
    new_x = x + displacement[0]
    new_y = y + displacement[1]
    light.set_data([new_x], [new_y])
    return new_x, new_y

def checkReflect(light,floor, ceil, cv):
    x_data, y_data = light.get_data()
    x = x_data[0]
    y = y_data[0]
    refFlg = False
    stopFlg = False
    if y > ceil:
        y = 2 * ceil - y
        refFlg = True
    if y < floor:
        y = 2 * floor + y
        refFlg = True
        stopFlg = True
    light.set_data([x], [y])
    if refFlg:
        cv[1] = -cv[1]
    return stopFlg
        
## 以下に共通変数を設定
# フォント設定
matplotlib.rc('font', family='MS Gothic')

# パラメータ設定
c = 1  # 光速（相対的な単位）
v = 0.6 * c  # 宇宙船の速度(光の速度の60%)
gamma = 1 / np.sqrt(1 - (v / c) ** 2)  # ローレンツ因子
c_r = 1  # 光速（ロケット内）
c_g = 1  # 光速（地上）
cv_r = [0,c]  # 光速進行方向（ロケット内）
cv_g = [v,c/gamma]  # 光速進行方向（地上）
global stop_r
global stop_g

L = 5  # 宇宙船の高さ
dt = 0.1  # 1フレームごとの時間ステップ
mode = "l" #　"galileo":「ガリレイ変換（光速加算）」or "lorentz":「ローレンツ変換（光速不変）」

# 図の設定
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# 宇宙船内の光の動き
ax[0].set_xlim(-2, 10)
ax[0].set_ylim(0, L)
ax[0].set_title("宇宙船内の光の動き")

# 地上から見た光の動き
ax[1].set_xlim(-2, 10)
ax[1].set_ylim(0, L)
ax[1].set_title("地上から見た光の動き")

# 宇宙船の描画
ship_rect = plt.Polygon(((-0.5, -0.5), (-0.5,0.5), (0.5,0.5), (0.8,0),(0.5,-0.5)),fill=True, color='gray')
ship_rect_g = plt.Polygon(((-0.5, -0.5), (-0.5,0.5), (0.5,0.5), (0.8,0),(0.5,-0.5)),fill=True, color='gray')

movePolygon(ship_rect,0,L/2)
movePolygon(ship_rect_g,0,L/2)

ax[0].add_patch(ship_rect)
ax[1].add_patch(ship_rect_g)

# 鏡の描画
top_mirror = ax[0].plot(0, L, 'ks', markersize=20)[0]
bottom_mirror = ax[0].plot(0, 0, 'ks', markersize=20)[0]

top_mirror_g = ax[1].plot(0, L, 'ks', markersize=20)[0]
bottom_mirror_g = ax[1].plot(0, 0, 'ks', markersize=20)[0]

# 光の描画
light, = ax[0].plot([], [], 'ro', markersize=12)
light_g, = ax[1].plot([], [], 'ro', markersize=12)

# 光の位置を初期化
light.set_data([0], [0])
light_g.set_data([0], [0])

# 時計
time_text_ship = ax[0].text(0, L * 0.8, "", fontsize=24, ha="left", color="blue")
time_text_ground = ax[1].text(0, L * 0.8, "", fontsize=24, ha="left", color="blue")

# stopFlg
stop_r = False
stop_g = False

# アニメーションの更新関数
def update(frame):
    global stop_r, stop_g  # グローバル変数を使うことを明示
    t = frame * dt  # 経過時間
    # 宇宙船の時計
    if stop_r == False:
        time_text_ship.set_text(f"時刻: {t:.1f} s")
        # 宇宙船内の光の動き
        moveC(light, dt, c_r, cv_r)
        stop_r = checkReflect(light ,0 ,L, cv_r)

    # 地上の時計
    if stop_g == False:
        time_text_ground.set_text(f"時刻: {t:.1f} s")
        # 地上から見た光の動き
        moveC(light_g, dt, c_g, cv_g)
        stop_g = checkReflect(light_g, 0, L, cv_g)
        # objectを動かす
        x_data, y_data = light_g.get_data()
        x = x_data[0]
        y = y_data[0]
        top_mirror_g.set_data([x], [L])
        bottom_mirror_g.set_data([x], [0])
        movePolygon(ship_rect_g,v*dt,0)

    return mode, light, light_g, time_text_ship, time_text_ground, top_mirror_g, bottom_mirror_g, ship_rect, ship_rect_g, stop_r, stop_g

def main():
    # アニメーション作成
    ani = animation.FuncAnimation(fig, update, frames=500, interval=200, repeat=False)
    plt.show()
    
if __name__ == "__main__":
    
    # コマンドライン引数（スクリプト名を除外）
    arguments = sys.argv[1:]
    
    # 引数を辞書に変換
    arg_dict = parse_arguments(arguments)
    
    mode = arg_dict.get("mode", "l") # g: galileo:「ガリレイ変換（光速加算）」or l: lorentz:「ローレンツ変換（光速不変）」
    type = arg_dict.get("type", "A") # A: 光の速度同じ B: 時間が同じ
    
    if mode == "g": #galileo:「ガリレイ変換（光速加算）
        cv_g = [v,c]  # 光速進行方向（地上）
        c_g = np.sqrt(v**2 +  c**2)
    elif mode == "l": #  lorentz:「ローレンツ変換（光速不変）」
        cv_g =  [v,c/gamma]  # 光速進行方向（地上）
        c_g = c

    main()
