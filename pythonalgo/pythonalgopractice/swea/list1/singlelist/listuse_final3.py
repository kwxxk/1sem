arr = [2,5,1,6,4,3]

total_sum = 0
for i in arr:
    total_sum +=i

print(total_sum)

max_val = float('-inf')
min_val = float('inf')

for i in arr:
    if i > max_val:
        max_val = i
    if i < min_val:
        min_val = i
print(max_val - min_val)