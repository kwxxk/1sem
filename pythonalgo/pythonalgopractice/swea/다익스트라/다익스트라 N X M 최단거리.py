import heapq
n , m = map(int,input().split())
MAP = [list(map(int,input().split()))
       for _ in range(n)]
dy = [-1,1,0,0]
dx = [0,0,-1,1]
def dijkstra():
    result = [[float('inf')] * m for _ in range(n)]
    result[0][0] = MAP[0][0]
    pq = [(MAP[0][0],0,0)]

    while pq:
        cost,y,x = heapq.heappop(pq)
        if result[y][x] < cost: continue

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]
            if not (0<=ny< n and 0<=nx <m): continue
            next_price = MAP[ny][nx]
            price_sum = cost + next_price

            if result[ny][nx] > price_sum:
                result[ny][nx] = price_sum
                heapq.heappush(pq,(price_sum,ny,nx))
    return result

a= n-1
b = m-1
answer = dijkstra()
print(answer[a][b])