# 이진트리의 DFS
#전위 순회
# 현재노드 -> 왼쪽자식노드 -> 오른쪽자식노드
bt = [ 0,'A','B','T','R','S','V']
bt += [0] * 100

# def dfs(now): #now는 현재노드
#
#     if bt[now] == 0: return
#
#     print(bt[now])
#     dfs(now * 2)
#     dfs(now * 2 +1)

# 중위 순회
# 왼쪽자식 -> 현재 -> 오른쪽 자식

# def dfs(now): #now는 현재노드
#
#     if bt[now] == 0: return
#     dfs(now*2)
#     print(bt[now])
#     dfs(now*2+1)



def dfs(now):
    if bt[now] ==0: return
    dfs(now*2)
    dfs(now*2+1)
    print(bt[now])

dfs(1)