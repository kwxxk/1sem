text = str(input())
answer = 0
step = 0
for step in range(len(text)):
    if text.find('[',step) or text.find('{',step):
        if text[step] == '[':
            end_point1 = text.find(']',step)
            answer += int(text[step+1:end_point1])
        elif text[step] == '{':
            end_point2 = text.find('}',step)
            answer *= int(text[step + 1:end_point2])
print(answer)