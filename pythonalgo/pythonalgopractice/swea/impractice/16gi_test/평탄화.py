t = int(input())
for test_case in range(1,t+1):
    n, k = map(int,input().split())
    top_arr = list(map(int,input().split()))
    dat = [0] * 1501
    for h in top_arr:
        dat[h] += 1
    high = max(top_arr)
    low = min(top_arr)

    for _ in range(k):
        # 1. 높이 차이가 1 이하라면 종료
        if high - low <= 1:break

        # 2. 가장 높은 탑에서 돌 1개 제거
        dat[high] -= 1
        dat[high - 1] += 1

        # 3. 가장 낮은 탑에 돌 1개 추가
        dat[low] -= 1
        dat[low + 1] += 1

        while dat[high] == 0:
            high -= 1

        while dat[low] == 0:
            low += 1

    answer = high - low

    print(f"#{test_case} {answer}")