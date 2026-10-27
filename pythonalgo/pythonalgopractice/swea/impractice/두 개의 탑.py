t = int(input())
for test_case in range(1,t+1):
    n, m1, m2 = map(int,input().split())
    block_weight = list(map(int,input().split()))
    block_weight.sort(reverse=True)
    cost = 0
    cntm1,cntm2 = 1,1
    for block in block_weight:
        if cntm1 <= m1 and (cntm2 > m2 or cntm1 <= cntm2):
            cost += cntm1 * block
            cntm1 += 1
        else:
            cost += cntm2 * block
            cntm2 += 1
    print(f"#{test_case} {cost}")
