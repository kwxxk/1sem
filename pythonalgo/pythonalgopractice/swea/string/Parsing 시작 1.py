text = 'helloworld[92084]answer'
idx1 = text.find('[')
idx2 = text.find(']')
print(text[idx1+1:idx2])