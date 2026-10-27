name = 'ABTQVX'

MAP = [
    [0,1,1,1,0,0],
    [0,0,0,0,1,1],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0]
]
n = int(input())
for i in range(6):
    if MAP[n][i] == 0: continue
    print(name[i])