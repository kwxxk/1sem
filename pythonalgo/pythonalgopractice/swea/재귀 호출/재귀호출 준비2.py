def num_print(a,b,c,d, i=1, j=1, k=1,l=1):
    if i > a:
        return
    print(i,j,k,l)
    if l < d:
        num_print(a,b,c,d,i,j,k,l+1)
    elif k < c:
        num_print(a,b,c,d,i,j,k+1,1)
    elif j < b:
        num_print(a,b,c,d,i,j+1,1,1)
    else:
        num_print(a,b,c,d,i+1,1,1,1)
num_print(3,3,3,3)

# def num_print(a,b,c,d):
#     for i in range(1,a+1):
#         for j in range(1,b+1):
#             for k in range(1,c+1):
#                 for l in range(1,d+1):
#                     print(i,j,k,l)
# num_print(3,3,3,3)