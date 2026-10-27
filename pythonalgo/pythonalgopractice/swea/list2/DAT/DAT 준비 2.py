a= [5,2,5,7,3]

n=int(input())

def get_count(n):
    cnt = 0
    for i in range(len(a)):
        if n == a[i]:
            cnt += 1
    return cnt

print(get_count(n))