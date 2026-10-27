t = int(input())
for test_case in range(1,t+1):
    n,m = map(int,input().split())
    matrix = [
        list(input().strip())
        for _ in range(n)
    ]
    cnt = 0
    dy = [1,-1,0,0]
    dx = [0,0,-1,1]
    positions = []
    for y in range(n):
        for x in range(m):
            if matrix[y][x] == 'L':
                positions.append((x,y))
    l_pos = set(positions)
    while l_pos:
        start = l_pos.pop()
        cnt +=1
        stack = [start]
        while stack:
            x,y = stack.pop()
            for z in range(4):
                nx = x+dx[z]
                ny = y+dy[z]
                if (nx,ny) in l_pos:
                    l_pos.remove((nx,ny))
                    stack.append((nx,ny))
    print(f"#{test_case} {cnt}")
