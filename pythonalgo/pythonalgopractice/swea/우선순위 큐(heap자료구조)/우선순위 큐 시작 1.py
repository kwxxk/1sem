import heapq

pq =[]

heapq.heappush(pq,(1,5))
heapq.heappush(pq,(0,2))
heapq.heappush(pq,(0,8))
heapq.heappush(pq,(1,1))
heapq.heappush(pq,(1,9))
heapq.heappush(pq,(0,4))
result = []
while pq:
    result.append(heapq.heappop(pq)[1])
print(*result)