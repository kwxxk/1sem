import heapq

MAP = [[0] * 6 for _ in range(6)]
MAP[0][1] = 5
MAP[0][2] = 10
MAP[0][3] = 7
MAP[0][5] = 12
MAP[1][0] = 5
MAP[1][5] = 9
MAP[2][5] = 1
MAP[3][2] = 2
MAP[3][4] = 1
MAP[4][5] = 3

def dijkstra(start,end):
    n = len(MAP)
    result = [float('inf')] * n
    result[start] = 0
    pq = [(0,start)]

    while pq:
        price,now = heapq.heappop(pq)
        if result[now] < price: continue

        for next_node in range(n):
            if MAP[now][next_node] == 0: continue
            next_price = MAP[now][next_node]
            price_sum = price + next_price

            if result[next_node] > price_sum:
                result[next_node] = price_sum
                heapq.heappush(pq,(price_sum,next_node))

    return result

sp, ep = input().split()
a = ord(sp) - ord('A')
b = ord(ep) - ord('A')
answer = dijkstra(a,b)
print(answer[b])