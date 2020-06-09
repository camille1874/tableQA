#import codecs
#import collections
#
#f_select = codecs.open("log_1216.txt", encoding="utf-8")
#f_spurious = codecs.open("spurious_analyze.txt", encoding="utf-8", mode="w")
###f_select = codecs.open("log_1208_model_align.txt", encoding="utf-8")
###f_x = codecs.open("test_x_1.txt", encoding="utf-8", mode="w")
###f_y = codecs.open("test_y_1.txt", encoding="utf-8", mode="w")
##f_x = codecs.open("test_x_multi.txt", encoding="utf-8", mode="w")
##f_y = codecs.open("test_y_multi.txt", encoding="utf-8", mode="w")
#
###add_lines = f_add.readlines()
#select_lines = f_select.readlines()
#
#spurious = collections.defaultdict(dict)
#
#item_id = 0
##j = 0
#i = 0
#targ = 0
#total = 0
#correct = 0
#
#while '*decoding:*' not in select_lines[i]:
#    i += 1
#
##for i in range(len(select_lines)):
#while i < len(select_lines):
#    if '*decoding:*' in select_lines[i]:
#        print("#" * 50)
#        get = False
#        item_id += 1
#        total += 1
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
#        j = 0
#        while i < len(select_lines) and 'selected_logical_form:' in select_lines[i]:
#            i += 1
#            selected = select_lines[i].split(" - ")[-1].strip()
#            warnings = []
#            while 'denotation_list' not in select_lines[i + 1]:
#                i += 1
#                if 'WARNING - weak_supervision' in select_lines[i]:
#                    warning = select_lines[i].split(" - ")[-1].strip().split(":")[0]
#                    warnings.append(warning)
#                if 'denotation_result' in select_lines[i + 1]:
#                    denotation_res = select_lines[i + 2].split(" - ")[-1].strip()
#                    break
#            else:
#                denotation = select_lines[i + 2].split(" - ")[-1].strip()
#                while 'target_list' not in select_lines[i + 3]:
#                    i += 1
#                target = select_lines[i + 4].split(" - ")[-1].strip()
#                while 'denotation_result' not in select_lines[i + 5]:
#                    i += 1
#                denotation_res = select_lines[i + 6].split(" - ")[-1].strip()
#            scores = tmp['candidates'][selected]
#            if denotation_res == 'True' and j != 0 and not get:
#                print('question:\n' + tmp['question'])
#                print('table:\n' + tmp['table'])
#                print('lgf:\n' + selected)
#                print('warnings:') 
#                print(warnings)
#                print('denotation:\n' + denotation)
#                print('scores:')
#                print(scores)
#                print('rank_score:')
#                print(scores[0] - scores[1])
#                print('#wrongly selected:')
#                print(tmp['selected'])
#                print('#scores:')
#                print(tmp['candidates'][tmp['selected']])
#                print('#rank_score')
#                print(tmp['candidates'][tmp['selected']][0] - 
#                        tmp['candidates'][tmp['selected']][1])    
#                get = True
#                targ += 1
#            if denotation_res == 'True' and warnings:
#                for w in warnings:
#                    spurious[w][selected] = {'question': tmp['question'], 'table': tmp['table']}
#
#
#            if j == 0:
#                tmp['selected'] = selected
#                tmp['result'] = denotation_res
#                if denotation_res == 'True':
#                    get = True
#                    correct += 1
#            j += 1
#            while i < len(select_lines) and 'selected_logical_form:' not in select_lines[i] and '*decoding' not in select_lines[i]:
#                i += 1
#        #if select_lines[i + 7].split("-")[-1].strip() == 'False' and tmp['candidates'][selected][1] == 1.0:
#        #print('*' * 50)
#        #print(tmp)
#        #for k,v in tmp.items():
#        #    print(k + ":")
#        #    print(v)
#        #res = 1 if select_lines[i + 7].split(" - ")[-1].strip() == 'True' else 0
#        #f_x.write(tmp['question'] + "\t")
#        #f_x.write(tmp['table'] + "\t")
#        #f_x.write(selected + "\t")
#        #f_x.write(str(tmp['candidates'][selected][0]) + "\n")
#        ##f_x.write(str(tmp['candidates'][selected][1]) + "\n")
#        ##f_y.write(str(res) + "\n")
#        
#        #if res == 1:
#        #    if tmp['candidates'][selected][1] == 1.0:
#        #        f_y.write('2\n')
#        #        type2 += 1
#        #    else:
#        #        f_y.write('1\n')
#        #        type1 += 1
#        #else:
#        #    f_y.write('0\n')
#        #    type0 += 1
#
#        #i += 2
#        #print('execute log:')
#        #while 'wikitables_variable_free_executor' in select_lines[i]:
#            #print(select_lines[i].split("-")[-1].strip())
#        #    i += 1
#        #i += 12
#        while i < len(select_lines) and '*decoding:*' not in select_lines[i]:
#            i += 1
#
#print("Total")
#print(total)
#print("Correct:")
#print(correct)
#print("Result:")
#print(correct / total)
#print("Wrongly ranked:")
#print(targ)
#print("Raw acc:")
#print((targ + correct) / total)
#
#
#idx = 1
#for k, v in spurious.items():
#    f_spurious.write(str(idx) + ") " + k + ":\n")
#    f_spurious.write("#" * 50 + "\n")
#    idx += 1
#    for kk, vv in v.items():
#        f_spurious.write(k + "--" + kk + ":\n")
#        for kkk, vvv in vv.items():
#            f_spurious.write(kkk + ": " + vvv + "\n")
#                
#        f_spurious.write("-" * 50 + "\n")
