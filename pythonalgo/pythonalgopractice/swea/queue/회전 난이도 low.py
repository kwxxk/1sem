t = int(input())
for test_case in range(1,t+1):
    n,m = map(int,input().split())
    arr = list(input().split())
    for i in range(m):
        value = arr.pop(0)
        arr.append(value)
    print(f"#{test_case} {arr[0]}")