arr = [
    [1,2,1,3,1],
    [2,2,2,2,2],
    [1,0,1,0,1],
    [3,1,2,1,3]
    ]
i, j = 1,2
plus_sum = 0

for d in range(1,2):
    plus_position = [
        (i - d, j),
        (i + d, j),
        (i, j - d),
        (i, j + d)
    ]
    for ni, nj in plus_position:
        if 0 <= ni <len(arr)  and 0 <= nj < len(arr[ni]):
            plus_sum += arr[ni][nj]
print(plus_sum)