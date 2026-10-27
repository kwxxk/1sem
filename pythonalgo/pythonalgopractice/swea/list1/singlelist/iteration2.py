n=int(input())
answer1 =''
answer2= ''

for _ in range(n):
    answer1 += '#'

for _ in range(n+5):
    answer2 += '!'

print(f"{answer1}\n{answer2}")