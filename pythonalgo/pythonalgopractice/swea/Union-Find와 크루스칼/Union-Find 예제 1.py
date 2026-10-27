boss = [i for i in range(10)]

def Find(n):
    if boss[n] == n: #가리키는 보스가 자기자신이면
        return n # final boss

    boss[n] = Find(boss[n]) # 경로압축
    return boss[n]

def Union(t1, t2):
    a = Find(t1) # t1의 보스가 a
    b = Find(t2) # t2의 보스가 b
    if a==b: return # 이미 보스가 같으면 탈락
    boss[b] = a # b의 보스가 a다

n = int(input())
for _ in range(n):
    a, b = map(int,input().split())
    Union(a,b)
m = int(input())
for _ in range(m):
    q1, q2 = map(int,input().split())
    if Find(q1) == Find(q2): print('O')
    else: print('X')
