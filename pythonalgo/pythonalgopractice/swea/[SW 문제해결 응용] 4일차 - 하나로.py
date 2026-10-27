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

t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    boss = [i for i in range(n)]
    edges = []
    arr_x = list(map(int,input().split()))
    arr_y = list(map(int,input().split()))
    e = float(input())
    for i in range(n):
        for j in range(i+1,n):
            s_dis = (arr_x[i]-arr_x[j]) ** 2 + (arr_y[i]-arr_y[j])**2
            cost = e * s_dis
            edges.append((cost,i,j))
    edges.sort()
    total = 0
    picked = 0

    for cost,a,b in edges:
        if Find(a) == Find(b): continue
        Union(a,b)
        total += cost
        picked += 1

        if picked == n - 1: break

    print(f"#{test_case} {int(total+0.5)}")