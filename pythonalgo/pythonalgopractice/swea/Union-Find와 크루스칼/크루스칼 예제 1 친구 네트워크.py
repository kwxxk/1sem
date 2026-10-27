def Find(x):
    if boss[x] == x: #가리키는 보스가 자기자신이면
        return x # final boss

    boss[x] = Find(boss[x]) # 경로압축
    return boss[x]

def Union(x, y):
    a = Find(x)
    b = Find(y)
    if a != b:
        boss[b] = a # b의 보스가 a다

m,n = map(int,input().split())
boss = [i for i in range(m)]
edges = []
for _ in range(m):
    a,b,cost = input().split()
    a = ord(a) - ord('A')
    b = ord(b) - ord('A')
    edges.append((int(cost),a,b))
edges.sort()

total = 0
picked = 0

for cost,a,b in edges:
    if Find(a) == Find(b): continue
    Union(a,b)
    total += cost
    picked +=1

    if picked == n-1: break

print(total)