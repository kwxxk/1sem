t = int(input())
for test_case in range(1,t+1):
    n,k = map(int,input().split())
    level = list(map(int,input().split()))
    # 정렬해서 k 차이 이하인 사람 수 최대로 해서 구하기
    team_len =[]
    level.sort()
    for i in range(n):
        for j in range(n-i):
            if level[i+j] - level[i] <= k:
                team_len.append(j+1)
    max_team = max(team_len)
    print(f"#{test_case} {max_team}")