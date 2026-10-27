arr = [[5,4,2,1],
       [3,7,7,7],
       [2,2,1,1]
       ]

for i in range(len(arr[0])):
    for j in range(len(arr)):
        print(arr[j][i], end=' ')
    print()