text = 'ABCDE'
char = input().split()
dat = [0] * 128

for ch in text:
    dat[ord(ch)] +=1
for ch in char:
    if dat[ord(ch)] > 0:
        print('O',end=' ')
    else:print('X',end=' ')