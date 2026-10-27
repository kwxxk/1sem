def is_p(text):
    return text == text[::-1]

# text = '우영우'
text = str(input())
print(int(is_p(text)))