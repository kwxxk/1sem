T = int(input())
for test_case in range(1,T+1):
    n = int(input())
    arr = list(map(int,input().split()))

    cnt = 0
    target = sorted(arr)
    while arr != target:
        start = cnt % 2
        for i in range(start,n-1,2):
            if arr[i] > arr[i+1]:
                arr[i],arr[i+1] = arr[i+1], arr[i]
        cnt += 1
    print(f"#{test_case} {cnt}")

