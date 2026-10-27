T = int(input())
for test_case in range(1,T+1):
    n = int(input())
    arr = list(map(int,input().split()))
    # len(arr) = n
    # i,j 가 n동안 다 순환
    answer = 0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            div_val = arr[i] % arr[j]
            answer += div_val

    print(f"#{test_case} {answer}")