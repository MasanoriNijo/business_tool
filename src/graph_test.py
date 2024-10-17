import matplotlib.pyplot as plt

# サンプルデータ
x = [1, 2, 3, 4, 5]
y = [2, 3, 5, 7, 11]

# 散布図を作成
plt.scatter(x, y, color='blue', label='Sample Data')

# グラフのタイトルとラベル
plt.title('Sample Scatter Plot')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# 凡例を表示
plt.legend()

# グラフを表示
plt.show()
