t= int(input())
for test_case in range(1,t+1):
    n = int(input())
    matrix = [
        list(map(int,input().split()))
        for _ in range(n)
    ]
    dy = [1,-1,0,0] #상 하 좌 우
    dx = [0,0,-1,1]
    # security_range = [
    #     [0] * n
    #     for _ in range(n)
    # ]

    for y in range(n):
        for x in range(n):
            if matrix[y][x] == 2:
                sc_y,sc_x = y,x
                for z in range(4):
                    for i in range(n):
                        scr_y = sc_y + dy[z] * i
                        scr_x = sc_x + dx[z] * i
                        if not (0 <= scr_y < n and 0 <= scr_x < n):
                            continue
                        if matrix[scr_y][scr_x] == 1:
                            break
                        matrix[scr_y][scr_x] = 3
    cnt = 0
    for row in matrix:
        for i in range(len(row)):
            if row[i] == 0:
                cnt +=1
    print(f"#{test_case} {cnt}")