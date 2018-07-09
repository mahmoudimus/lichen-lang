def good(t):
    a, b, c = t

def bad(t):
    a = t.__get_single_item_unchecked__(0)

t = 1, 2, 3
good(t)
bad(t)
