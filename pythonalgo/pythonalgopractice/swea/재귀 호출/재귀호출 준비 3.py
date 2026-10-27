def num_print(i,n):
    if i > n:
        return

    print(i, end=' ')
    num_print(i+1,n)
    print(i, end=' ')

num_print(0,5)