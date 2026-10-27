arr = [
    [1,5,10,15],
    [15,15,20,30]
    ]

dat = [0] * 31
idx = 0

for i in range(len(arr)):
    for j in range(len(arr[i])):
        val = arr[i][j]
        dat[val] += 1


n = int(input())
print(dat[n])