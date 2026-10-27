text = 'B[45]AB[9994]'

st_idx_1 = text.find('[')
st_idx_2 = text.find('[',st_idx_1+1)
end_idx_1 = text.find(']')
end_idx_2 = text.find(']',end_idx_1+1)

num1 = int(text[st_idx_1+1:end_idx_1])
num2 = int(text[st_idx_2+1:end_idx_2])

print(num1+num2)