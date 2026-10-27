n = int(input())

used_col = [0] * n
used_diag1 = [0] * (2 * n - 1)
used_diag2 = [0] * (2 * n - 1)
answer = 0

def dfs(row):
    global answer

    if row == n:
        answer +=1
        return

    for col in range(n):
        diag1 = row + col
        diag2 = row - col + n - 1

        if used_col[col] or used_diag1[diag1] or used_diag2[diag2]: continue

        used_col[col] = 1
        used_diag1[diag1] = 1
        used_diag2[diag2] = 1
        dfs(row + 1)
        used_col[col] = 0
        used_diag1[diag1] = 0
        used_diag2[diag2] = 0

dfs(0)
print(answer)