import heapq

pq =[]

heapq.heappush(pq,5)
heapq.heappush(pq,2)
heapq.heappush(pq,8)
heapq.heappush(pq,1)
heapq.heappush(pq,9)
result = []
while pq:
    result.append(heapq.heappop(pq))
print(result)