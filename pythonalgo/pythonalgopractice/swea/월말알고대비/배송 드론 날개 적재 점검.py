t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    weight = list(map(int,input().split()))
    pair = []
    answer = 1
    for i in range(n//2):
        p_weight = weight[i] + weight[n-1-i]
        pair.append(p_weight)
    for j in range(len(pair)-1):
        if pair[j] >= pair[j+1]:
            answer = 0
    print(f"#{test_case} {answer}")
