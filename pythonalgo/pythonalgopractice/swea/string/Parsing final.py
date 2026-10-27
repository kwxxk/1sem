arr = [
    'GOLDABCGOLD',
    'HELLOWORLD',
    'WHITEGOLD'
]

def get_find(text):
    step = 0
    cnt = 0
    while True:
        idx = text.find('GOLD', step)
        if idx == -1:
            break
        step = idx + 4
        cnt += 1
    return cnt
total = 0
for text in arr:
    total += get_find(text)
print(total)

