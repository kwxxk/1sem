from collections import deque

name = 'ACBQTPR'

MAP = [[0] * 7 for _ in range(7)]
MAP[0][1] = 1
MAP[0][2] = 1
MAP[0][3] = 1
MAP[2][4] = 1
MAP[3][5] = 1
MAP[3][6] = 1

q = deque()
q.append(0) # 출발점

while q:
    # 1. 큐에서 뺀다
    now = q[0]
    q.popleft()
    print(name[now], end = ' ')
    # 2. 다음 갈 곳 예약 걸기
    for i in range(7):
        if MAP[now][i] == 0: continue
        q.append(i)