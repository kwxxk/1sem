t = int(input())
for test_case in range(1,t+1):
    code = input()
    stack = []
    pairs = {
        ')': '(',
        '}': '{'
    }
    result = 1
    for ch in code:

        if ch == '(' or ch == '{':
            stack.append(ch)
        elif ch  == ')' or ch == '}':
            if not stack:
                result = 0
                break
            if stack[-1] != pairs[ch]:
                result = 0
                break
            stack.pop()
    if stack:
        result = 0
    print(f"#{test_case} {result}")