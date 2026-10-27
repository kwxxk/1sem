n= int(input())

if n % 2 == 0:
    for i in range(6):
        print(n+2*i, end=' ')
else:
    for i in range(11):
        print(n+3*i, end=' ')