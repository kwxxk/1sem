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

n = int(input())
boss = [i for i in range(26)]
edges = []
for _ in range(n):
    a,b = input().split()
    a = ord(a) - ord('A')
    b = ord(b) - ord('A')
    edges.append((a,b))

team_cnt = 0
personal_cnt = 0
group_cnt = [0] * 26
for a,b in edges:
    if Find(a) == Find(b): continue
    Union(a,b)
for i in range(len(boss)):
    group_cnt[Find(i)] += 1
for size in group_cnt:
    if size > 1: team_cnt +=1
    elif size == 1: personal_cnt +=1

print(team_cnt)
print(personal_cnt)