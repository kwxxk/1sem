T = int(input())
for test_case in range(1,T+1):
    n, p = map(int, input().split())
    matrix = [
        list(map(int,input().split()))
        for _ in range(n)
    ]
    dy = [-1, 1, 0, 0]
    dx = [0, 0, -1, 1]
    max_virus = 0
    for y in range(n):
        for x in range(n):
            sum_virus = matrix[y][x]
            for z in range(4):
                for power in range(1,p+1):
                    ny = y + dy[z] * power
                    nx = x + dx[z] * power

                    if ny < 0 or nx <0 or ny >=n or nx >=n: continue
                    sum_virus += matrix[ny][nx]
            max_virus = max(max_virus,sum_virus)

    print(f"#{test_case} {max_virus}")