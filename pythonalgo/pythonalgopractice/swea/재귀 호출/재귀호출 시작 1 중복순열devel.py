selected = []
def num_print(level):
    if level == 3:
        print(*selected)
        return

    for number in range(1, 7):
        selected.append(number)
        num_print(level + 1)
        selected.pop()
num_print(0)