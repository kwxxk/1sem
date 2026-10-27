arr = [
    [1,2,1,3,1],
    [2,2,2,2,2],
    [1,0,1,0,1],
    [3,1,2,1,3]
    ]

y, x = map(int,input().split())
cross_sum = arr[y][x]

dy = [-1, -1, 1, 1]  # 행 이동: 좌상 우상 우상 우하
dx = [-1, 1, -1, 1]  # 열 이동

for k in range(4):
    cy = y + dy[k]
    cx = x + dx[k]

    if 0 <= cy < len(arr) and 0 <= cx < len(arr[cy]):
        cross_sum *= arr[cy][cx]


print(cross_sum)