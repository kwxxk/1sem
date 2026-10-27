from collections import deque

alist = [[] for _ in range(7)]

alist[0] = [1,2]
alist[1] = [3]
alist[2] = [4]
alist[4] = [5,6]

q = deque()
q.append(0) #출발점

name = "ABCDEFG"

while q:
    # 1. 큐에서 뺀다(탐색)
    now = q[0] # top
    q.popleft()
    print(name[now], end = ' ')

    # 2. 다음 갈 곳 예약 걸기 (큐 등록)
    for i in range(len(alist[now])):
        next_node = alist[now][i]
        q.append(next_node)