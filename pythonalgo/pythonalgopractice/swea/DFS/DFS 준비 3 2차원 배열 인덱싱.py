arr = []
arr.append([]) # 4,2,5,1,1
arr.append([]) # 3,4,2
arr.append([])
arr.append([]) #1,1,2,3
arr[0].append(4)
arr[0].append(2)
arr[0].append(5)
arr[0].append(1)
arr[0].append(1)

arr[1].append(3)
arr[1].append(4)
arr[1].append(2)

arr[3].append(1)
arr[3].append(1)
arr[3].append(2)
arr[3].append(3)


for row in arr:
    print(row)
