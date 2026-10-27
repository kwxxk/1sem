t= int(input())
for test_case in range(1,t+1):
    n = int(input())
    matrix = [
        list(map(int,input().split()))
        for _ in range(n+1)
    ]
    max_d_square = 0
    houses = []
    for y in range(n+1):
        for x in range(n+1):
            if matrix[y][x] == 2:
                pos_y,pos_x = y,x
            elif matrix[y][x] == 1:
                houses.append((y,x))
    for hy,hx in houses:
        d_square = (hy-pos_y)**2 + (hx-pos_x)**2
        max_d_square = max(max_d_square, d_square)
    r = int(max_d_square ** 0.5)
    if r ** 2 < max_d_square:
        r+=1
    print(f"#{test_case} {int(r)}")
