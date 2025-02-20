import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib

matplotlib.rc('font', family='MS Gothic')

# パラメータ設定
c = 1  # 光速（相対的な単位）
v = 0.6 * c  # 宇宙船の速度
L = 5  # 宇宙船の高さ
frames = 100  # アニメーションのフレーム数
dt = 0.1  # 1フレームごとの時間ステップ
T = 2 * L / c  # 光が宇宙船内を1往復する時間

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

# 地上の時計（固定）
time_text_ground = ax[1].text(1, L * 0.8, f"時刻: 0.0 s", fontsize=12, ha="center", color="blue")

# アニメーションの更新関数
def update(frame):
    t = frame * dt  # 経過時間
    t_mod = t % T  # 光の周期での時間

    # 光の反射処理（上下移動）
    if t_mod < T / 2:
        y = (t_mod / (T / 2)) * L  # 上昇
    else:
        y = L - ((t_mod - T / 2) / (T / 2)) * L  # 下降（反射）

    # 宇宙船内の光の動き
    light.set_data([0], [y])

    # 地上から見た光の動き（宇宙船の移動を考慮）
    x_g = v * t
    light_g.set_data([x_g], [y])

    # 宇宙船内の時計を更新
    time_text_ship.set_text(f"時刻: {t:.1f} s")
    time_text_ship.set_position((0, L * 0.8))

    return light, light_g, time_text_ship

# アニメーション作成
ani = animation.FuncAnimation(fig, update, frames=frames, interval=50, blit=True)
plt.show()
