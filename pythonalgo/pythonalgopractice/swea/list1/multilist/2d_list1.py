arr = [[0 for i in range(4)] for j in range(4)]
arr[0][0] = 7
arr[1][3] = 1
arr[2][1] = 3
arr[3][3] = 9
for row in arr:
    print(*row)
