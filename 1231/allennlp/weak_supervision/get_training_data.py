#import codecs
#import collections
#
#f_select = codecs.open("log_1205_train.txt", encoding="utf-8")
##f_select = codecs.open("log_1208_model_align_train.txt", encoding="utf-8")
##f_new = codecs.open("train_classification_1.txt", encoding="utf-8", mode="w")
#f_new = codecs.open("train_multi.txt", encoding="utf-8", mode="w")
#
##add_lines = f_add.readlines()
#select_lines = f_select.readlines()
#
#item_id = 0
##j = 0
#i = 0
#
#while '*decoding:*' not in select_lines[i]:
#    i += 1
#
#type2 = 0
#type1 = 0
#type0 = 0
#
##for i in range(len(select_lines)):
#while i < len(select_lines):
#    if '*decoding:*' in select_lines[i]:
#        item_id += 1
#        tmp = {}
#        tmp['question'] = select_lines[i + 5].split(" - ")[-1].strip()
#        tmp['table'] = select_lines[i + 7].split(" - ")[-1].strip()
#        i += 1
#        #j += 1
#        while '*decoding:*' not in select_lines[i] and 'selected_logical_form:' not in select_lines[i]:
#            rec = {}
#            while 'selected_logical_form:' not in select_lines[i]:
#                rec[select_lines[i + 8].split(" - ")[-1].strip()] = (float(select_lines[i + 2].split(" - ")[-1].strip()), float(select_lines[i + 10].split(" - ")[-1].strip()))
#                #rec[select_lines[i + 8].split(" - ")[-1].strip()] = (float(select_lines[i + 2].split(" - ")[-1].strip()), float(select_lines[i + 11].split(" - ")[-1].strip()))
#                i += 11
#                #i += 12
#            tmp['candidates'] = rec
#        selected = select_lines[i + 1].split(" - ")[-1].strip()
#        #if select_lines[i + 7].split("-")[-1].strip() == 'False' and tmp['candidates'][selected][1] == 1.0:
#        #print('*' * 50)
#        #print(tmp)
#        #for k,v in tmp.items():
#        #    print(k + ":")
#        #    print(v)
#        res = 1 if select_lines[i + 7].split(" - ")[-1].strip() == 'True' else 0
#        f_new.write(tmp['question'] + "\t")
#        f_new.write(tmp['table'] + "\t")
#        f_new.write(selected + "\t")
#        f_new.write(str(tmp['candidates'][selected][0]) + "\t")
#        #f_new.write(str(tmp['candidates'][selected][1]) + "\t")
#        #f_new.write(str(res) + "\n")
#        
#        if res == 1:
#            if tmp['candidates'][selected][1] == 1.0:
#                f_new.write('2\n')
#                type2 += 1
#            else:
#                f_new.write('1\n')
#                type1 += 1
#        else:
#            f_new.write('0\n')
#            type0 += 1
#        
#
#
#        i += 2
#        #print('execute log:')
#        while 'wikitables_variable_free_executor' in select_lines[i]:
#            #print(select_lines[i].split("-")[-1].strip())
#            i += 1
#        #i += 12
#        while i < len(select_lines) and '*decoding:*' not in select_lines[i]:
#            i += 1
#
#print(type2)
#print(type1)
#print(type0)
