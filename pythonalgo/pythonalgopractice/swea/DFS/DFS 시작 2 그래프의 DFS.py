alist = [
    [] for _ in range(4)
]
alist[0] = [1,3]
alist[1] = [2]
alist[2] = [0,3]
alist[3] = [2]
visited = [False] * 4
def dfs(now):
    visited[now] = True
    print(now)
    for i in range(len(alist[now])):
        next_node = alist[now][i]
        if visited[next_node] == False:
            dfs(next_node)

dfs(0)