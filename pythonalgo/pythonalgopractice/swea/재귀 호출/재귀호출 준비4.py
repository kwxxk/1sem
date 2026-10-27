def tree(level, max_level):
    if level > max_level:
        return

    tree(level+1,max_level)
    tree(level+1,max_level)
    print(level)

tree(0,2)