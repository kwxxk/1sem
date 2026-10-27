arr = [9,5,1,15,7,3]
arr2=[]
for i in range(len(arr)):
    arr2.append(arr[len(arr)-1-i])

print(*arr2)