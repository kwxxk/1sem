import heapq

MAP = [[0] * 6 for _ in range(6)]
MAP[0][1] = 15
MAP[0][3] = 22
MAP[1][2] = 5
MAP[2][3] = 6
MAP[2][4] = 2
MAP[3][5] = 7
MAP[4][5] = 1

def dijkstra(start):
    n = len(MAP) #노드의 갯수
    result = [float('inf')] * n
    result[start] = 0 # 시작노드
    # pq초기화
    pq = [(0,start)] # 비용, 노드

    while pq:
        # 1. 힙에서 뺸다(탐색)
        price, now = heapq.heappop(pq)

        # 더 큰값 나오면 continue
        if result[now] < price: continue

        # 다음 갈 곳 예약
        for i in range(n):
            if MAP[now][i] == 0: continue
            next_price = MAP[now][i] # 다음 노드 비용
            price_sum = price + next_price # 비용을 누적

            # 더 작은 값 나오면 갱신
            if result[i] > price_sum:
                result[i] = price_sum
                # 힙 등록
                heapq.heappush(pq, (price_sum, i))

    return result

result = dijkstra(0)
print(*result)