arr = [0 for _ in range(8)]
# for i in range(4):
#     arr[i] = 7
# for i in range(4,8):
#     arr[i] = 15
arr = [7 if i < 4 else 15 for i in range(8)]
print(*arr)