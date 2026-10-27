from collections import deque

def bfs(start):
    q = deque()
    visited = [0] * 10
    # start 출발점
    q.append(start)
    # 시작점 방문 처리
    visited[start] = 1

    while q:
        # 1. 큐에서 뺀다
        now = q[0] # top
        print(chr(now + ord('A')), end = ' ')
        q.popleft()

        # 2. 다음 갈곳 예약 걸기
        for i in range(len(alist[now])):
            next = alist[now][i]
            # 이미 방문 했으면 continue
            if visited[next] == 1: continue
            # 방문 표시
            visited[next] = 1
            q.append(next)
            # 방문 기록을 지우지 않습니다.
            # visited[next] = 0

alist = [[] for _ in range(6)]
alist[0] = [1, 2]
alist[1] = [0, 2]
alist[2] = [0, 1, 3]
alist[3] = [2, 4]
alist[4] = [3]

n = int(input())
bfs(n)