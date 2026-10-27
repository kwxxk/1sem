arr = list(map(int, input().split()))
cnt = 0

for val in arr:
    if val == 7:
        cnt +=1
print(cnt)