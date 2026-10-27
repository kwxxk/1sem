# a,b = map(int,input().split())
# arr = [
#     [0] * 5
#     for _ in range(5)
# ]
#
# for y in range(5):
#     for x in range(5):
#         arr[y][x] = abs(a-y) + abs(b-x) + 1
# for row in arr:
#     print(*row)
from collections import deque

a, b = map(int, input().split())

arr = [
    [0] * 5
    for _ in range(5)
]

dy = [-1, 1, 0, 0]
dx = [0, 0, -1, 1]

queue = deque()

arr[a][b] = 1
queue.append((a, b))

while queue:
    current_y, current_x = queue.popleft()

    for direction in range(4):
        next_y = current_y + dy[direction]
        next_x = current_x + dx[direction]

        if 0 <= next_y < 5 and 0 <= next_x < 5:
            if arr[next_y][next_x] == 0:
                arr[next_y][next_x] = arr[current_y][current_x] + 1
                queue.append((next_y, next_x))

for row in arr:
    print(*row)