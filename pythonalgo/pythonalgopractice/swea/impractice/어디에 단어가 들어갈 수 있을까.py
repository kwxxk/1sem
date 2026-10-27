t = int(input())
for test_case in range(1,t+1):
    n,k = map(int,input().split())
    matrix = [
        list(map(int,input().split()))
        for _ in range(n)
    ]
    #
    cnt = 0
    for y in range(n):
        length = 0
        for x in range(n):
            if matrix[y][x] == 1:
                length += 1
            else:
                if length == k:
                    cnt += 1
                length = 0

        if length == k:
            cnt +=1
    for x in range(n):
        length = 0
        for y in range(n):
            if matrix[y][x] == 1:
                length += 1
            else:
                if length == k:
                    cnt += 1
                length = 0

        if length == k:
            cnt += 1
    print(f"#{test_case} {cnt}")

