name = 'DUSRK'

# MAP = [
#     [0,1,0,1,1],
#     [0,0,1,1,0],
#     [0,0,0,0,0],
#     [0,0,1,0,1],
#     [0,1,0,1,0]
# ]
#인접행렬
# n = int(input())
# for i in range(5):
#     if MAP[n][i] == 0: continue
#     print(name[i])

#인접 리스트
alist = [
    [] for _ in range(5)
]
alist[0] = [1,3,4]
alist[1] = [2,3]
alist[3] = [2,4]
alist[4] = [1,3]

num = int(input())
for i in range(len(alist[num])):
    print(name[alist[num][i]])
