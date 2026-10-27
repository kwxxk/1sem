T = int(input())
for test_case in range(1,T+1):
    n, m = map(int, input().split())
    matrix = [
        list(map(int,input().split()))
        for _ in range(n)
    ]
    dy = [-1, 1, 0, 0]
    dx = [0, 0, -1, 1]
    max_flower = 0
    for y in range(n):
        for x in range(m):
            plus_sum = matrix[y][x]

            for distance in range(1,matrix[y][x]+1):
                for z in range(4):
                    ny = y + dy[z] * distance
                    nx = x + dx[z] * distance
                    if ny < 0 or nx < 0 or ny >= n or nx >= m: continue
                    plus_sum += matrix[ny][nx]
                max_flower = max(max_flower,plus_sum)
    print(f"#{test_case} {max_flower}")