t= int(input())
for test_case in range(1,t+1):
    n,k = map(int,input().split())
    sample_arr = list(map(int,input().split()))
    passcode_arr = list(map(int,input().split()))
    step = 0
    answer = []
    for i in range(len(sample_arr)):
        if sample_arr[i] == passcode_arr[step]:
            answer.append(passcode_arr[step])
            step += 1
        if step == k:
            break
    if passcode_arr == answer:
        print(f"#{test_case}", 1)
    else:
        print(f"#{test_case}", 0)
