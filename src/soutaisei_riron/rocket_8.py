import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import sys

def movePolygon(polygon, x, y):
    newXY = [[xy[0] + x, xy[1] + y] for xy in polygon.get_xy()]
    polygon.set_xy(newXY)

def moveC(light, dt, v, vc):
    x_data, y_data = light.get_data()
    x, y = x_data[0], y_data[0]
    norm = np.linalg.norm(vc)
    if norm == 0:
        raise ValueError("方向ベクトル vc がゼロベクトルです。")
    unit_vc = vc / norm
    displacement = unit_vc * v * dt
    new_x, new_y = x + displacement[0], y + displacement[1]
    light.set_data([new_x], [new_y])
    return new_x, new_y

def checkReflect(light, floor, ceil, cv):
    x_data, y_data = light.get_data()
    x, y = x_data[0], y_data[0]
    refFlg, stopFlg = False, False
    if y > ceil:
        y = 2 * ceil - y
        refFlg = True
    if y < floor:
        y = 2 * floor - y
        refFlg = True
        stopFlg = True
    light.set_data([x], [y])
    if refFlg:
        cv[1] = -cv[1]
    return stopFlg

# 設定
c = 1  # 光速
v = 0.6 * c  # 宇宙船の速度
L = 5  # 宇宙船の高さ
gamma = 1 / np.sqrt(1 - (v / c) ** 2)
dt = 0.1
mode = "l"

# 光を逆方向に放つ
cv_r = [0, -c]
cv_g = [v, -c / gamma]
stop_r, stop_g = False, False

fig, ax = plt.subplots(1, 2, figsize=(12, 5))
ax[0].set_xlim(-2, 10)
ax[0].set_ylim(-L, L)
ax[0].set_title("宇宙船内の光の動き")
ax[1].set_xlim(-2, 10)
ax[1].set_ylim(-L, L)
ax[1].set_title("地上から見た光の動き")

# 宇宙船
ship_rect = plt.Polygon(((-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.8, 0), (0.5, -0.5)), fill=True, color='gray')
ship_rect_g = plt.Polygon(((-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.8, 0), (0.5, -0.5)), fill=True, color='gray')
movePolygon(ship_rect, 0, L / 2)
movePolygon(ship_rect_g, 0, L / 2)
ax[0].add_patch(ship_rect)
ax[1].add_patch(ship_rect_g)

# 光の描画
light, = ax[0].plot([], [], 'ro', markersize=12)
light_g, = ax[1].plot([], [], 'ro', markersize=12)
light.set_data([0], [L])
light_g.set_data([0], [L])

def update(frame):
    global stop_r, stop_g
    t = frame * dt
    if not stop_r:
        moveC(light, dt, c, cv_r)
        stop_r = checkReflect(light, -L, L, cv_r)
    if not stop_g:
        moveC(light_g, dt, c, cv_g)
        stop_g = checkReflect(light_g, -L, L, cv_g)
        movePolygon(ship_rect_g, v * dt, 0)
    return light, light_g, ship_rect_g

def main():
    ani = animation.FuncAnimation(fig, update, frames=500, interval=200, repeat=False)
    plt.show()

if __name__ == "__main__":
    main()
