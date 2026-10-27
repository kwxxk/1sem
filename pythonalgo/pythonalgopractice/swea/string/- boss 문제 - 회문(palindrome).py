def find_palindrome(matrix, n, m, test_case):
    for y in range(n):
        for x in range(n - m + 1):
            for i in range(m // 2):
                if matrix[y][x + i] != matrix[y][x + m - 1 - i]:
                    break
            else:
                print(f"#{test_case}", ''.join(matrix[y][x:x + m]))
                return

    for y in range(n - m + 1):
        for x in range(n):
            for i in range(m // 2):
                if matrix[y + i][x] != matrix[y + m - 1 - i][x]:
                    break
            else:
                print(f"#{test_case}", ''.join(matrix[y + j][x] for j in range(m)))
                return

t = int(input())
for test_case in range(1,t+1):
    n,m = map(int,input().split())
    matrix = [
        list(input().strip())
        for _ in range(n)
    ]
    find_palindrome(matrix, n, m, test_case)



