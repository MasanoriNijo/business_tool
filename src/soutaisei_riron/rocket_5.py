import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import sys

matplotlib.rc('font', family='MS Gothic')

# コマンド引数で「ガリレイ変換（光速加算）」or「ローレンツ変換（光速不変）」を選択
if len(sys.argv) > 1 and sys.argv[1] == "galileo":
    mode = "galileo"  # 光速が加算される（ガリレイ変換）
else:
    mode = "lorentz"  # 光速が一定（ローレンツ変換）

# パラメータ設定
c = 1  # 光速（相対的な単位）
v = 0.6 * c  # 宇宙船の速度
L = 5  # 宇宙船の高さ
frames = 100  # アニメーションのフレーム数
dt = 0.1  # 1フレームごとの時間ステップ

gamma = 1 / np.sqrt(1 - (v / c) ** 2)  # ローレンツ因子

# 図の設定
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# 宇宙船内の光の動き
ax[0].set_xlim(-2, 2)
ax[0].set_ylim(0, L)
ax[0].set_title("宇宙船内の光の動き")

# 地上から見た光の動き
ax[1].set_xlim(-2, 2 + v * (frames * dt))
ax[1].set_ylim(0, L)
ax[1].set_title("地上から見た光の動き")

# 宇宙船の描画
ship_rect = plt.Rectangle((-1, 0), 2, L, fill=False, color='gray')
ax[0].add_patch(ship_rect)

# 鏡の描画
top_mirror = ax[0].plot(0, L, 'ks', markersize=10)[0]
bottom_mirror = ax[0].plot(0, 0, 'ks', markersize=10)[0]

top_mirror_g = ax[1].plot(0, L, 'ks', markersize=10)[0]
bottom_mirror_g = ax[1].plot(0, 0, 'ks', markersize=10)[0]

# 光の描画
light, = ax[0].plot([], [], 'ro', markersize=5)
light_g, = ax[1].plot([], [], 'ro', markersize=5)

# 宇宙船内の時計（動く）
time_text_ship = ax[0].text(0, L * 0.8, "", fontsize=12, ha="center", color="blue")

# 地上の時計（動く）
time_text_ground = ax[1].text(1, L * 0.8, "", fontsize=12, ha="center", color="blue")

# アニメーションの更新関数
def update(frame):
    t = frame * dt  # 経過時間
    T_ship = 2 * L / c  # 宇宙船内の光の往復時間
    T_ground = gamma * T_ship  # 地上から見た光の往復時間

    # 宇宙船内での光の動き（反射）
    t_mod = t % T_ship
    if t_mod < T_ship / 2:
        y = (t_mod / (T_ship / 2)) * L  # 上昇
    else:
        y = L - ((t_mod - T_ship / 2) / (T_ship / 2)) * L  # 下降（反射）

    # 地上から見た光の動き（光速の扱いによって変化）
    x_g = v * t
    if mode == "galileo":
        # ガリレイ変換（光速が v + c / v - c になる）
        c_eff = c + v if (t_mod < T_ship / 2) else c - v
        y_g = (t_mod / (T_ship / 2)) * L if t_mod < T_ship / 2 else L - ((t_mod - T_ship / 2) / (T_ship / 2)) * L
    else:
        # ローレンツ変換（光速は常に c）
        y_g = y

    # 宇宙船内の光の動き
    light.set_data([0], [y])

    # 地上から見た光の動き
    light_g.set_data([x_g], [y_g])

    # 宇宙船の時計
    time_text_ship.set_text(f"時刻: {t:.1f} s")
    
    # 地上の時計
    time_text_ground.set_text(f"時刻: {t / gamma:.1f} s")  # 宇宙船の時間が遅れる

    return light, light_g, time_text_ship, time_text_ground

# アニメーション作成
ani = animation.FuncAnimation(fig, update, frames=frames, interval=1000, blit=True)
plt.show()
