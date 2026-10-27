import heapq

pq = []

# 2-1. heappush할때 음수로
heapq.heappush(pq, -5)
heapq.heappush(pq, -2)
heapq.heappush(pq, -8)
heapq.heappush(pq, -1)
heapq.heappush(pq, -9)

# print(pq) # 힙트리구조
result = []
while pq:
    # 2-2. heappop한 후 다시 -를 붙여서
    result.append(-heapq.heappop(pq))

print(result)