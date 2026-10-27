t = int(input())
for test_case in range(1,t+1):
    code = input().split()
    num_stack = []
    error = False
    for val in code:
        if val == '.':
            break
        if val.isdigit():
            num_stack.append(int(val))
        else:
            if len(num_stack) < 2:
                error = True
                break
            right = num_stack.pop()
            left = num_stack.pop()

            if val == '+':
                result = left + right
            elif val == '-':
                result = left - right
            elif val == '*':
                result = left * right
            elif val == '/':
                result = left // right
            else:
                error = True
                break
            num_stack.append(result)
    if error or len(num_stack) != 1:
        print(f"#{test_case} error")
    else:
        print(f"#{test_case} {num_stack[0]}")