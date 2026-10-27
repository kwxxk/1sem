arr = [1,3,2,-5]
n = int(input())
arr[0] = n
arr[-1] = arr[1] + arr[2]

print(*arr)
