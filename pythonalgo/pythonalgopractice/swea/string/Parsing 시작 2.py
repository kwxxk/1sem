arr = [
    'ABCQ',
    'B[4]R',
    'CCDA',
    'BT[15]'
]
def get_find(text):

    start_idx = text.find('[')
    end_idx = text.find(']')
    if start_idx != -1 and end_idx > start_idx:
        num = int(text[start_idx+1:end_idx])
        print(num, end=' ')

for text in arr:
    get_find(text)

