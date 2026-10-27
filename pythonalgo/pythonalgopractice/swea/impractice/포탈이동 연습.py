t = int(input())
for test_case in range(1,t+1):
    n= int(input())
    arr = list(map(int,input().split()))
    dat = [0] * n
    current = 0
    while current != n-1:
        first_visit = (dat[current] == 0)
        dat[current] +=1
        if current == 0: current +=1
        elif first_visit: current = arr[current] -1
        else: current +=1

    print(f"#{test_case} {sum(dat)}")