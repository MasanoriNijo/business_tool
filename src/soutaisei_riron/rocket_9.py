import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import sys

def parse_arguments(args):
    arg_dict = {}
    for arg in args:
        if ":" in arg:
            key, value = arg.split(":", 1)
            arg_dict[key] = value
    return arg_dict

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

def checkReflect(light, left_wall, right_wall, cv):
    x_data, y_data = light.get_data()
    x = x_data[0]
    refFlg = False
    if x < left_wall:
        x = 2 * left_wall - x
        refFlg = True
    if x > right_wall:
        x = 2 * right_wall - x
        refFlg = True
    light.set_data([x], [y_data[0]])
    if refFlg:
        cv[0] = -cv[0]

def main():
    matplotlib.rc('font', family='MS Gothic')
    
    c = 1  # 光速
    v = 0.6 * c  # ロケットの速度
    gamma = 1 / np.sqrt(1 - (v / c) ** 2)
    c_r = 1  # ロケット内の光速
    c_g = 1  # 地上の光速
    cv_r = [-c, 0]  # ロケット内の光速ベクトル（右から左へ）
    cv_g = [-c / gamma, 0]  # 地上から見た光速ベクトル（ローレンツ変換）
    L = 5  # ロケットの幅
    dt = 0.1
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].set_xlim(0, L)
    ax[0].set_ylim(-2, 2)
    ax[0].set_title("ロケット内の光の動き")
    ax[1].set_xlim(0, L)
    ax[1].set_ylim(-2, 2)
    ax[1].set_title("地上から見た光の動き")
    
    ship_rect = plt.Polygon(((0, -0.5), (0, 0.5), (L, 0.5), (L, -0.5)), fill=True, color='gray')
    ship_rect_g = plt.Polygon(((0, -0.5), (0, 0.5), (L, 0.5), (L, -0.5)), fill=True, color='gray')
    ax[0].add_patch(ship_rect)
    ax[1].add_patch(ship_rect_g)
    
    left_wall = ax[0].plot(0, 0, 'ks', markersize=20)[0]
    right_wall = ax[0].plot(L, 0, 'ks', markersize=20)[0]
    left_wall_g = ax[1].plot(0, 0, 'ks', markersize=20)[0]
    right_wall_g = ax[1].plot(L, 0, 'ks', markersize=20)[0]
    
    light, = ax[0].plot([], [], 'ro', markersize=12)
    light_g, = ax[1].plot([], [], 'ro', markersize=12)
    
    light.set_data([L], [0])
    light_g.set_data([L], [0])
    
    time_text_ship = ax[0].text(L * 0.8, 1, "", fontsize=24, ha="left", color="blue")
    time_text_ground = ax[1].text(L * 0.8, 1, "", fontsize=24, ha="left", color="blue")
    
    def update(frame):
        t = frame * dt
        time_text_ship.set_text(f"時刻: {t:.1f} s")
        time_text_ground.set_text(f"時刻: {t:.1f} s")
        moveC(light, dt, c_r, cv_r)
        moveC(light_g, dt, c_g, cv_g)
        checkReflect(light, 0, L, cv_r)
        checkReflect(light_g, 0, L, cv_g)
        movePolygon(ship_rect_g, v * dt, 0)
        return light, light_g, time_text_ship, time_text_ground, ship_rect_g
    
    ani = animation.FuncAnimation(fig, update, frames=500, interval=200, repeat=False)
    plt.show()

if __name__ == "__main__":
    main()
