name = 'BTAR'

MAP = [
    [0,0,0,0],
    [1,0,0,0],
    [1,1,0,0],
    [1,1,0,0]
]

n = int(input())
for i in range(4):
    if MAP[n][i] == 0: continue
    print(name[i])