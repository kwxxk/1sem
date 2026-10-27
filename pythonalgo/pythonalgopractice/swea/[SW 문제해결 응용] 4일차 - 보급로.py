import heapq
def dijkstra():
    result = [[float('inf')] * n for _ in range(n)]
    result[0][0] = MAP[0][0]
    pq = [(MAP[0][0],0,0)]

    while pq:
        depth,y,x = heapq.heappop(pq)
        if result[y][x] < depth: continue

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if not (0<=ny< n and 0<=nx <n): continue
            next_depth = MAP[ny][nx]
            depth_sum = depth + next_depth

            if result[ny][nx] > depth_sum:
                result[ny][nx] = depth_sum
                heapq.heappush(pq,(depth_sum,ny,nx))
    return result

dy = [-1,1,0,0]
dx = [0,0,-1,1]
t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    MAP = [list(map(int,input().strip()))
           for _ in range(n)]
    a= n-1
    answer = dijkstra()
    print(f"#{test_case} {answer[a][a]}")