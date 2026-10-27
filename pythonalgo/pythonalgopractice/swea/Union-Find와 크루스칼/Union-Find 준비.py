boss = [i for i in range(10)]

def Find(n):
    if boss[n] == n: #가리키는 보스가 자기자신이면
        return n # final boss

    result = Find(boss[n]) # 재귀호출
    boss[n] = result # 경로압축
    return result

def Union(t1, t2):
    a = Find(t1) # t1의 보스가 a
    b = Find(t2) # t2의 보스가 b
    if a==b: return # 이미 보스가 같으면 탈락
    boss[b] = a # b의 보스가 a다

Union(6,7)
Union(5,6)
Union(1,2)


a, b = map(int,input().split())
# logic : 보스가 같으면 같은 그룹.
if Find(a) == Find(b): print('O')
else: print('X')
