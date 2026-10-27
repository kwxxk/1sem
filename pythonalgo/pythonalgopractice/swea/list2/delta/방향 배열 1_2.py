arr = [
    [1,2,1,3,1],
    [2,2,2,2,2],
    [1,0,1,0,1],
    [3,1,2,1,3]
    ]

i, j = 1, 2
plus_sum = 0

di = [-1, 1, 0, 0]  # 행 이동: 위, 아래, 왼쪽, 오른쪽
dj = [0, 0, -1, 1]  # 열 이동

for k in range(4):
    ni = i + di[k]
    nj = j + dj[k]

    if 0 <= ni < len(arr) and 0 <= nj < len(arr[ni]):
        plus_sum += arr[ni][nj]

print(plus_sum)