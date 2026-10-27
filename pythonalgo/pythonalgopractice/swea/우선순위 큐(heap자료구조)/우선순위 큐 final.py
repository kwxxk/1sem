import heapq

pq = []

heapq.heappush(pq,(2,'BHC'))
heapq.heappush(pq,(1,'NeNe'))
heapq.heappush(pq,(3,'KFC'))
heapq.heappush(pq,(1,'BBQ'))
heapq.heappush(pq,(2,'Moms'))
heapq.heappush(pq,(4,'Mc'))

while len(pq) >= 2:
    item1 = heapq.heappop(pq)
    item2 = heapq.heappop(pq)
    new = (item1[0]+item2[0],min(item1[1],item2[1]))
    heapq.heappush(pq,new)
print(f"{pq[0][1]} {pq[0][0]}")