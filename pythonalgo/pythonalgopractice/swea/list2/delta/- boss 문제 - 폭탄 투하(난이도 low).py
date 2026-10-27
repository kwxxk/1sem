arr = [['_' for _ in range(5)] for _ in range(4)]
# 상 하 좌 우 좌상 좌하 우상 우하
dy = [-1, 1, 0, 0, -1, 1, -1, 1]
dx = [0, 0, -1, 1, -1, -1, 1, 1]

points = []

for _ in range(2):
    y, x = map(int, input().split())
    points.append((y, x))

(y1, x1), (y2, x2) = points

for k in range(8):
    shap_y = y1 + dy[k]
    shap_x = x1 + dx[k]
    if 0 <= shap_y< len(arr) and 0 <= shap_x < len(arr[shap_y]):
        arr[shap_y][shap_x] = '#'

for b in range(8):
    shap_y = y2 + dy[b]
    shap_x = x2 + dx[b]
    if 0 <= shap_y < len(arr) and 0 <= shap_x < len(arr[shap_y]):
        arr[shap_y][shap_x] = '#'
for row in arr:
    print(*row)