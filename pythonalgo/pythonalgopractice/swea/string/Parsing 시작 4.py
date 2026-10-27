text = 'ABCDEFABCKKKKKABC'

cnt = 0
step = 0
while True:
    idx = text.find('ABC',step)
    if idx == -1:
        break
    step = idx + 3
    cnt += 1
print(cnt)
