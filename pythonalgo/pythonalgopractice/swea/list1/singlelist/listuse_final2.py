arr = []
a,b = map(int, input().split())

arr = [
    a if i<3
    else b if i<5
    else a+b
    for i in range(8)
]
print(*arr)