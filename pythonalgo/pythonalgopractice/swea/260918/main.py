import sys
sys.stdin=open("input.txt","r")
sys.stdout=open("output.txt","w")
for _ in range(10):
    tc=int(input())
    arr= [
        list(map(int,input().split()))
        for _ in range(100)
    ]
    ans = 0

    print(f"#{tc} {ans}")