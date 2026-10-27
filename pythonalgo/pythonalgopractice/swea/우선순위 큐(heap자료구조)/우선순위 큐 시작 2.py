import heapq

pq =[]

heapq.heappush(pq,('A',-7))
heapq.heappush(pq,('C',-9))
heapq.heappush(pq,('C',-7))
heapq.heappush(pq,('D',-6))
heapq.heappush(pq,('A',-5))
while pq:
    item = heapq.heappop(pq)
    print(f"({-item[1]}, {item[0]})", end = ' ')