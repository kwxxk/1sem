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
n = int(input())
arr = [
    list(map(int,input().split()))
    for _ in range(n)
]
a,b = map(int,input().split())
visited = [0] * n
max_cost = float('-inf')
min_cost = float('inf')
visited[a] = 1
dfs(a,0)
print(min_cost)
print(max_cost)

