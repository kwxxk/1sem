# name = '0123'
#
# MAP = [
#     [0,0,0,0],
#     [1,0,0,1],
#     [0,0,1,1],
#     [0,0,0,0]
# ]
# n = int(input())
# for i in range(4):
#     if MAP[n][i] == 0: continue
#     print(name[i])

arr = list([] for _ in range(4))
arr[1] = [0,3]
arr[2] = [1,3]

print(arr)