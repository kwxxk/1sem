t = int(input())
for test_case in range(1,t+1):
    n=int(input())
    target_pattern = list(map(int,input().split()))
    led = [0] * (n)
    cnt = 0
    for i in range(n):
        if target_pattern[i] != led[i]:
            cnt += 1
            for multiple in range(i, n , i+1):
                led[multiple] ^= 1
    print(f"#{test_case} {cnt}")
