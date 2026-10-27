arr = [[0] * 6 for _ in range(6)]

arr[0][1] = 2
arr[0][2] = 6
arr[0][3] = 3
arr[1][0] = 2
arr[1][2] = 7
arr[1][3] = 4
arr[2][0] = 6
arr[2][1] = 7
arr[3][2] = 2
arr[3][0] = 3
arr[3][1] = 4
arr[4][5] = 7
arr[4][2] = 1

visited = [0] * 6

def dfs(now):
    visited[now] = 1
    print(now, end = ' ')
    for next_node in range(len(arr[now])):
        if arr[now][next_node] != 0 and visited[next_node] ==0:
            dfs(next_node)
dfs(4)