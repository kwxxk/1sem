T = int(input())
for test_case in range(1,T+1):
    n, m = map(int, input().split())

    matrix = []

    for _ in range(n):
        row = list(map(int, input().split()))
        matrix.append(row)
    max_fly = 0
    for i in range(n):
        for j in range(n):
            plus_sum = matrix[i][j]
            cross_sum = matrix[i][j]

            for d in range(1,m):
                plus_position = [
                    (i-d,j),
                    (i+d,j),
                    (i,j-d),
                    (i,j+d)
                ]
                for ni, nj in plus_position:
                    if 0 <= ni < n and 0 <= nj < n:
                        plus_sum += matrix[ni][nj]

                croos_position = [
                    (i-d,j+d), #좌상
                    (i+d,j+d), #우상
                    (i-d,j-d), #좌하
                    (i+d,j-d) #우하
                ]
                for ci, cj in croos_position:
                    if 0 <= ci < n and 0 <= cj <n:
                        cross_sum += matrix[ci][cj]

            current_fly = max(plus_sum,cross_sum)
            if current_fly > max_fly:
                max_fly = current_fly
    print(f"#{test

    _case} {max_fly}")