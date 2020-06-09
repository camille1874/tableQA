#a = "(mode_string (argmax (argmin all_rows number_column:album) number_column:album) string_column:album)"
#a = "(sum (first (first all_rows)) num2_column:win)"
a = "(count (argmax (next (previous all_rows)) num2_column:released))"
#a = "(count (next (previous all_rows)))"
#a = "(select_string (previous (next (first all_rows))) string_column:affiliates)"
print(a)
#targ = "first (first"
#targ = "argmax (argmin"
#idx = a.split("(").index(targ.split("(")[0])
#tmp = a.split("(")
#tmp.pop(idx)
#res = "(".join(tmp)
#tmp = res.split(")")
#tmp.pop(-idx - 1)
#res = ")".join(tmp)
#print(res)

import re
targ = "(next (previous"
p = " \\(next \\(previous[^\\(\\)]*\\)\\)"
if re.findall(p, a):
    print("here")
    a = re.sub(p, "",a)
else:
    idx = len(a[:a.find(targ)].split("("))
    tmp = a.split("(")
    tmp.pop(idx)
    tmp.pop(idx)
    res = "(".join(tmp)
    tmp = res.split(")")
    tmp.pop(-idx - 1)
    tmp.pop(-idx - 1)
    a = ")".join(tmp)
print(a)
