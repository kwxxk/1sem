t= int(input())
for test_case in range(1,t+1):
    n,s = map(int,input().split())
    point_arr = list(map(int,input().split()))
    point_arr.sort()
    start_point = [s]
    if abs(s - max(point_arr)) < abs(s - min(point_arr)):
        sp_arr = start_point + point_arr[::-1]

    else: sp_arr = start_point + point_arr
    result = 0
    for i in range(len(sp_arr)-1):
        result += abs(sp_arr[i+1] - sp_arr[i])

    print(f"#{test_case} {result}")