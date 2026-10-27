t = int(input())
for test_case in range(1,t+1):
    arr = list(map(int,input().split()))
    cnt = 0
    a,b,c = arr[0],arr[1],arr[2]

    while b >= c:
        b -= 1
        cnt += 1
    while a >= b:
        a -= 1
        cnt+=1
    if a < 1: print(f"#{test_case} -1")
    else: print(f"#{test_case} {cnt}")