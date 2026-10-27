def num_print(a,b,c, i=1, j=1, k=1):
    if i > a:
        return
    print(i,j,k)
    if k < c:
        num_print(a,b,c,i,j,k+1)
    elif j < b:
        num_print(a,b,c,i,j+1,1)
    else:
        num_print(a,b,c,i+1,1,1)

num_print(6,6,6)