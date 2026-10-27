bt = [0,9,4,12,3,6,0,15,0,0,0,0,0,0,13,17]
bt += [0] * 100
#전위순회
# def front_dfs(now):
#     if bt[now] == 0: return
#     print(bt[now],end = ' ')
#     front_dfs(2*now)
#     front_dfs(2*now+1)
#
# front_dfs(1)

# 중위순회
# def mid_dfs(now):
#     if bt[now] == 0: return
#     mid_dfs(2*now)
#     print(bt[now], end = ' ')
#     mid_dfs(2*now+1)
#
# mid_dfs(1)

#후위 순회
def rear_dfs(now):
    if bt[now] == 0: return
    rear_dfs(2*now)
    rear_dfs(2*now+1)
    print(bt[now], end = ' ')
rear_dfs(1)