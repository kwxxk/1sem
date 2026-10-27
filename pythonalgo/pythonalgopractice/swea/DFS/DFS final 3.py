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
a,b = map(int,input().split())
cnt = 0
def dfs(now):
    global cnt
    if now == b:
        cnt += 1
        return
    visited[now] = 1

    for next_node in range(len(arr)):
        if arr[now][next_node] !=0 and visited[next_node] == 0:
            dfs(next_node)
    visited[now] = 0
dfs(a)
print(cnt)
