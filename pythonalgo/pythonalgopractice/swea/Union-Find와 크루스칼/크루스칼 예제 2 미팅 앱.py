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

n, m = map(int,input().split())
types = input().split()
boss = [i for i in range(n+1)]
edges = []
for _ in range(m):
    u,v,d = map(int,input().split())
    edges.append((d,u,v))
edges.sort()

total = 0
picked = 0

for d,u,v in edges:
    if types[u-1] == types[v-1]: continue
    if Find(u) == Find(v): continue
    Union(u,v)
    total += d
    picked +=1

    if picked == n-1: break

if picked == n-1: print(total)
else: print(-1)
