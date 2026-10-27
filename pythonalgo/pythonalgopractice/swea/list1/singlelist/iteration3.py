n=int(input())
answer = ''
if n > 10:
    # print('#' * 5)
    for _ in range(5):
        answer += '#'
else:
    # print('#' * n)
    for _ in range(n):
        answer += '#'
print(answer)