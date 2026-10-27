A = [5,7,5,4,2,9]
B = [5,4,2,5,6]

def is_exist(n):
    return n in B

for val in A:
    if is_exist(val): print("O",end=" ")
    else: print("X",end=" ")

