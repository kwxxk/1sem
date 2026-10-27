arr = [
    [1,2,1,3,1],
    [2,2,2,2,2],
    [1,0,1,0,1],
    [3,1,2,1,3]
    ]

i, j = map(int,input().split())
position = []

dy = [0, 0, 1, 1]   # 0, 0, 아래쪽, 아래쪽
dx = [1, -1, 0, 1]   # 우, 좌, 0, 우

for k in range(4):
    cy = i + dy[k]
    cx = j + dx[k]

    if 0 <= cy < len(arr) and 0 <= cx < len(arr[cy]):
        position.append(arr[cy][cx])


print(max(position))