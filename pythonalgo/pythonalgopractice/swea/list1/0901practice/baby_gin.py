def is_baby_gin(arr):
    arr.sort()
    group_cnt = 0

    def is_triplet():
        nonlocal group_cnt
        for i in range(len(arr)-2):
            if arr[i] == arr[i+1] == arr[i+2]:
                group_cnt +=1
                del arr[i:i+3]
                return True
        return False

    def is_run():
        nonlocal group_cnt
        for i in range(len(arr)-2):
            if arr[i+1] == (arr[i]+arr[i+2])/2:
                group_cnt +=1
                del arr[i:i + 3]
                return True
            return False
    while group_cnt < 2:
        found = is_triplet()

        if group_cnt < 2:
            found = is_run() or found
        if not found:
            break
    return group_cnt == 2

arr = list(map(int,input().split()))
if is_baby_gin(arr):
    print("Yes")
else:
    print("No")
