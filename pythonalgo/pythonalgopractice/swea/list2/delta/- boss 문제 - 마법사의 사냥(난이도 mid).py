n = int(input())
matrix = []

for _ in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)
# matrix = [
#     list(map(int, input().split()))
#     for _ in range(n)
# ]
k = int(input()) # 마법 시전 범위

dy = [-1,1,-1,1] #좌상 좌하 우상 우하
dx = [-1,-1,1,1]
max_sum = 0
for y in range(n):
    for x in range(n):
        cross_sum = 0
        for d in range(1,k+1):
            for z in range(4):
                cy = y + dy[z] * d
                cx = x + dx[z] * d

                if 0 <= cy < len(matrix) and 0 <= cx < len(matrix[cy]):
                    cross_sum += matrix[cy][cx]
        max_sum = max(max_sum, cross_sum)
print(max_sum)