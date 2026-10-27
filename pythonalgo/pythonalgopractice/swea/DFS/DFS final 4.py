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
max_cost = float('-inf')
min_cost = float('inf')
visited[a] = 1
def dfs(now,cost):
    global max_cost, min_cost
    if now == b:
        if cost > max_cost: max_cost = cost
        if cost < min_cost: min_cost = cost
        return
    for next_node in range(len(arr)):
        if arr[now][next_node] !=0 and visited[next_node] == 0:
            visited[next_node] = 1
            dfs(next_node,cost+arr[now][next_node])
            visited[next_node] = 0

dfs(a,0)
print(max_cost)
print(min_cost)
