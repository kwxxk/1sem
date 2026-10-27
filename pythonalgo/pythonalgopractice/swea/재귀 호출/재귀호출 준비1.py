# def forprint(n,m):
#     for i in range(1,n+1):
#         for j in range(1,m+1):
#             print(i,j)
#
# forprint(3,3)

def arr_print(n,m, i=1,j=1):
    if i > n:
        return
    print(i,j)
    if j < m:
        arr_print(n,m,i,j+1)
    else:
        arr_print(n,m,i+1,1)

arr_print(3,3)