from collections import deque

n, m = map(int,input().split())
routes = [[] for _ in range(n + 1)]

for _ in range(m):
    a, b = map(int, input().split())
    routes[a].append(b)
    routes[b].append(a)
r, k = map(int,input().split())

visited = [0] * (n+1)
q = deque([(r,0)])
visited[r] = 1
cnt =1

while q:
    now,ride = q.popleft()

    for next in routes[now]:
        if not visited[next]:
            visited[next] = 1
            q.append((next,ride+1))
            if ride + 1 <= k: cnt +=1
print(cnt)