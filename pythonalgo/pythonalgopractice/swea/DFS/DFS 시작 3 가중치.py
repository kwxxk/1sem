MAP = [
    [0,7,20,8],
    [0,0,5,0],
    [15,0,0,0],
    [0,0,6,0]
]

n = int(input())
visited = [False] * 4
visited[0] = True
def dfs(now,cost):
    if now == n:
        print(cost)
        return
    for next_node in range(len(MAP)):
        if MAP[now][next_node] !=0 and not visited[next_node]:
            visited[next_node] = True
            dfs(next_node,cost+MAP[now][next_node])
            visited[next_node] = False
dfs(0,0)