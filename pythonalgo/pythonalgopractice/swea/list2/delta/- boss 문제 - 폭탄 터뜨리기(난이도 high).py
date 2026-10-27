n,m = map(int, input().split())
k = int(input())
matrix = [
    list(input().strip())
    for _ in range(n)
]
# 상 하 좌 우
dy = [-1,1,0,0]
dx = [0,0,-1,1]
positions = []
for bomb_y in range(n):
    for bomb_x in range(m):
        if matrix[bomb_y][bomb_x] == '@':
            positions.append((bomb_y,bomb_x))
for bomb_y,bomb_x in positions:
    matrix[bomb_y][bomb_x] == '%'
    for z in range(4):
        for bomb_dis in range(k + 1):
            bomb_range_y = bomb_y + dy[z] * bomb_dis
            bomb_range_x = bomb_x + dx[z] * bomb_dis
            if not (0 <= bomb_range_y < n and 0 <= bomb_range_x < m):
                continue
            if matrix[bomb_range_y][bomb_range_x] == '#':
                break
            matrix[bomb_range_y][bomb_range_x] = '%'



for row in matrix:
    print(*row,sep='')

