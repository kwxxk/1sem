name = 'ABTQVX'

arr = [[0] * len(name) for _ in range(len(name))]
arr[0][1] = 1
arr[0][2] = 1
arr[0][3] = 1
arr[1][4] = 1
arr[1][5] = 1

def dfs(now):
    print(now, end = ' ')
    for j in range(len(arr)):
        # if arr[now][j] == 1:
        #     dfs(j)
        if arr[now][j] == 0: continue
        dfs(j)
dfs(0)