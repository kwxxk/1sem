T = int(input())

for test_case in range(1, T + 1):
    N = int(input())
    boxes = list(map(int, input().split()))

    max_fall = 0

    for i in range(N):
        count = 0

        for j in range(i + 1, N):
            if boxes[i] > boxes[j]:
                count += 1

        if count > max_fall:
            max_fall = count

    print(f"#{test_case} {max_fall}")