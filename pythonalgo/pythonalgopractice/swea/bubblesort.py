def BubbleSort(a,N):
    for i in range(N-1):
        for j in range(N - i - 1):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                
            else:
                a[j], a[j+1] = a[j], a[j+1]
    return a
a = [12, 3, 9,1,15,7]
print(BubbleSort(a,len(a)))