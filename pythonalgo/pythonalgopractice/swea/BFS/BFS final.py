from collections import deque

def bfs(start,end):
    q = deque()
    visited = [0] * 5
    # start 출발점
    q.append((start,0))
    # 시작점 방문 처리
    visited[start] = 1
    while q:
        (now, level) = q[0]
        q.popleft()
        if now == end:
            print(level)
            return
        for i in range(len(alist[now])):
            next_node = alist[now][i]
            if alist[now][i] == 1 and visited[i] == 0:
                visited[i] = 1
                q.append((i,level+1))

alist = [
    [0,1,0,0,1],
    [0,0,0,1,1],
    [1,0,0,0,0],
    [1,0,1,0,0],
    [0,0,0,0,0]
]
a,b = map(int,input().split())
bfs(a,b)
