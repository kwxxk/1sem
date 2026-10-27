n = int(input())

arr = [['#' for _ in range(n)] for _ in range(n)]

for row in arr:
    print(''.join(row))
# for i in range(n):
#     for j in range(n):
#         print('#', end='')
#     print()