t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    arr = [
        list(map(int,input().split()))
        for _ in range(n)
    ]
    cnt = 0
    for i in range(n-1):
        for j in range(i+1,n):
            a_diff = arr[i][0] - arr[j][0]
            b_diff = arr[i][1] - arr[j][1]
                  if a_diff * b_diff < 0:
                cnt += 1
    print(f"#{test_case} {cnt}")
