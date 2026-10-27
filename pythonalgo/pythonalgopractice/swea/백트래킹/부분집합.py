def dfs(idx, total):
    if total > s: return
    if idx == n:
        if total == s:
            print(*chosen)
        return
    chosen.append(element[idx])
    dfs(idx+1, total + element[idx])
    chosen.pop()

    dfs(idx +1,total)


n = int(input())
element = list(map(int,input().split()))
s = int(input())
chosen = []
dfs(0,0)
