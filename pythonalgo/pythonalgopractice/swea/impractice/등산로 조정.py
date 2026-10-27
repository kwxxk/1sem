t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    matrix =[
        list(map(int,input().split()))
        for _ in range(n)
    ]
    #상하좌우
    max_cnt = 0
    dy = [-1,1,0,0]
    dx = [0,0,-1,1]
    for start_y in range(n):
        for start_x in range(n):
            cnt = 1 #초기 자리시작 1
            current_y = start_y
            current_x = start_x
            while True:
                lowest = matrix[current_y][current_x]
                next_y = -1
                next_x = -1
                for z in range(4):
                    pos_y = current_y + dy[z]
                    pos_x = current_x + dx[z]
                    if 0<= pos_y<n and 0<= pos_x <n:
                        if matrix[pos_y][pos_x] < lowest:
                            lowest = matrix[pos_y][pos_x]
                            next_y = pos_y
                            next_x = pos_x
                if next_y == -1:
                    break
                current_y = next_y
                current_x = next_x
                cnt += 1
            max_cnt = max(max_cnt,cnt)
    print(f"#{test_case} {max_cnt}")
                        # 이동하고 cnt +=1, 반복해서 maxcnt 갱신