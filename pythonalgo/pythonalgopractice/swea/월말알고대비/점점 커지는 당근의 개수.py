t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    c = list(map(int,input().split()))
    cnt = 1
    max_cnt = 1
    for i in range(1,len(c)):
        if c[i-1] < c[i]:
            cnt +=1
        else: cnt = 1
        max_cnt = max(max_cnt,cnt)
    print(f"#{test_case} {max_cnt}")