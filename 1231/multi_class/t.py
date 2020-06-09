import codecs
f = codecs.open("train_classification_1.txt", encoding="utf-8")
#f = codecs.open("test_raw.txt", encoding="utf-8")
#f_pos = codecs.open("test_pos.txt", encoding="utf-8", mode="w")
#f_neg = codecs.open("test_neg.txt", encoding="utf-8", mode="w")
f_pos = codecs.open("train_pos_1.txt", encoding="utf-8", mode="w")
f_neg = codecs.open("train_neg_1.txt", encoding="utf-8", mode="w")
#f_targ = codecs.open("test_x.txt", encoding="utf-8", mode="w")

lines = f.readlines()
for l in lines:
    items = l.split("\t")
    if items[-1].strip() == '1':
        #f_pos.write(items[0] + "\t" + items[1] + "\t" + items[2] + "\n")
        f_pos.write("\t".join(items[:-1]) + "\n")
    else:
        #f_neg.write(items[0] + "\t" + items[1] + "\t" + items[2] + "\n")
        f_neg.write("\t".join(items[:-1]) + "\n")
    #f_targ.write(items[0] + "\t" + items[1] + "\t" + items[2] + "\n")
