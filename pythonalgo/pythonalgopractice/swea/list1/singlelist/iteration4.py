arr = list(map(int,input().split()))
a= arr[0]
b= arr[1]
if a <= b:
    for i in range(a,b+1):
        print(i, end=' ')

else:
    for i in range(a,b-1,-1):
        print(i, end= ' ')

