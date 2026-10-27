t = int(input())
for test_case in range(1,t+1):
    n, k_min, k_max = map(int,input().split())
    si = list(map(int,input().split()))
    dat = [0] * 101

    for score in si:
        dat[score] += 1
    for score in range(1,101):
        dat[score] += dat[score-1]

    min_difference = float('inf')

    for t1 in range(1,100):
        for t2 in range(t1+1,101):
            class_c = dat[t1-1]
            class_b = dat[t2-1] - dat[t1-1]
            class_a = n- dat[t2-1]

            if(
                k_min<=class_a <=k_max
                and k_min<=class_b<=k_max
                and k_min<=class_c<=k_max
            ):
                max_num = max(class_a,class_b,class_c)
                min_num = min(class_a,class_b,class_c)

                difference = max_num - min_num
                min_difference = min(difference,min_difference)

    if min_difference == float('inf'):
        answer = -1
    else: answer = min_difference

    print(f"#{test_case} {answer}")