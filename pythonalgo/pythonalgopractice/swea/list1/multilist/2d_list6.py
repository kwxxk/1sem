arr = [list(map(int, input().split())) for _ in range(4)]

for i in arr[::-1]:
    print(*i[::-1])