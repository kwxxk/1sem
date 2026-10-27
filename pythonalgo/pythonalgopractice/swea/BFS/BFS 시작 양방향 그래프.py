from collections import deque

alist = [[] for _ in range(5)]

alist[0] = [1,2]
alist[1] = [0,2]
alist[2] = [0,1,3]
alist[3] = [2,4]
alist[4] = [3]
visited = [0] * 5

q = deque()
n = int(input())
q.append(n) #출발점
visited[n] = 1
name = "ABCDE"
while q:
    # 1. 큐에서 뺀다(탐색)
    now = q[0] # top
    q.popleft()
    print(name[now], end = ' ')

    # 2. 다음 갈 곳 예약 걸기 (큐 등록)
    for i in range(len(alist[now])):
        next_node = alist[now][i]
        if visited[next_node] == 0:
            q.append(next_node)
            visited[next_node] = 1