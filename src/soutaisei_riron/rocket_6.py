import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import sys

matplotlib.rc('font', family='MS Gothic')

# コマンドライン引数で変換の種類を指定
use_galilean = len(sys.argv) > 1 and sys.argv[1] == "galileo"

# パラメータ設定
c = 1  # 光速（相対的な単位）
v = 0.6 * c  # 宇宙船の速度
L = 5  # 宇宙船の高さ
frames = 50  # アニメーションのフレーム数

# 図の設定
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].set_xlim(-2, 2)
ax[0].set_ylim(0, L)
ax[1].set_xlim(-2, 2 + v * (frames / 10))
ax[1].set_ylim(0, L)
ax[0].set_title("宇宙船内の光の動き")
ax[1].set_title("地上から見た光の動き")

# 宇宙船の描画
ship_rect = plt.Rectangle((-1, 0), 2, L, fill=False, color='gray')
ax[0].add_patch(ship_rect)

# 鏡と時計の位置
top_mirror = ax[0].plot(0, L, 'ks', markersize=10)[0]
bottom_mirror = ax[0].plot(0, 0, 'ks', markersize=10)[0]

top_mirror_g = ax[1].plot([], [], 'ks', markersize=10)[0]
bottom_mirror_g = ax[1].plot([], [], 'ks', markersize=10)[0]

# 光の動き
light, = ax[0].plot([], [], 'ro', markersize=5)
light_g, = ax[1].plot([], [], 'ro', markersize=5)

# アニメーションの更新関数
def update(frame):
    t = frame / 10  # 時間のスケール調整
    y = t * c % (2 * L)  # 上下に移動
    if int(t * c / (2 * L)) % 2 == 1:
        y = 2 * L - y  # 反射の処理
    
    # 宇宙船内での光の動き
    light.set_data([0], [y])
    
    # 地上から見た場合
    x_g = v * t  # 宇宙船の移動による x 座標
    y_g = y
    if use_galilean:
        # ガリレイ変換: 速度を単純加算
        y_g = (t * c) % (2 * L)
        if int(t * c / (2 * L)) % 2 == 1:
            y_g = 2 * L - y_g
    
    light_g.set_data([x_g], [y_g])
    
    # 鏡の位置も光と同調させる
    top_mirror_g.set_data([x_g], [L])
    bottom_mirror_g.set_data([x_g], [0])
    
    return light, light_g, top_mirror_g, bottom_mirror_g

# アニメーション作成
ani = animation.FuncAnimation(fig, update, frames=frames, interval=50, blit=True)
plt.show()