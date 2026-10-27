arr = [list(map(int, input().split())) for _ in range(5)]

cnt = 0
max_val = float('-inf')
min_val = float('inf')
total_sum = 0
for row in arr:
    for value in row:
        if value == 2:
            cnt +=1
        if max_val < value:
            max_val = value
        if min_val > value:
            min_val = value

for i in range(len(arr)):
    total_sum += arr[i][i]

print(cnt)
print(max_val,min_val)
print(total_sum)