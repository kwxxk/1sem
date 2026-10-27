t = int(input())
for test_case in range(1,t+1):
    chars = input().strip()
    stack = []

    for ch in chars:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)

    answer = len(stack)
    print(f"#{test_case} {answer}")