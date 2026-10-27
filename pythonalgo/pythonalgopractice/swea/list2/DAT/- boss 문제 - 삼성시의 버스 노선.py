t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    matrix = [
        list(map(int, input().split()))
        for _ in range(n)
    ]
    p = int(input())
    c_arr = [int(input()) for _ in range(p)]

    dat = [0] * 5001
    for row in matrix:
        a,b = row
        for stop in range(a,b+1):
            dat[stop] += 1
    print(f"#{test
    _case}", *(dat[c] for c in c_arr))