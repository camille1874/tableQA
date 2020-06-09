#import codecs
#import collections
#
#f_select = codecs.open("./log_1203_nodrop_select.txt", encoding="utf-8")
#f_add = codecs.open("./log_1203_nodrop_add.txt", encoding="utf-8")
#
#select_lines = f_select.readlines()
#add_lines = f_add.readlines()
#
#item_id = 0
#j = 0
#i = 0
#
#while '*decoding:*' not in select_lines[i]:
#    i += 1
#
#while '*decoding:*' not in add_lines[j]:
#    j += 1
#
##for i in range(len(select_lines)):
#while i < len(select_lines) and j < len(add_lines):
#    if '*decoding:*' in select_lines[i]:
#        tmp = {}
#        tmp['question'] = select_lines[i + 5].split("-")[-1].strip()
#        tmp['table'] = select_lines[i + 7].split("-")[-1].strip()
#        i += 1
#        j += 1
#        while '*decoding:*' not in select_lines[i] and 'selected_logical_form:' not in select_lines[i]:
#            rec = {}
#            while 'selected_logical_form:' not in select_lines[i]:
#                rec[select_lines[i + 8].split("-")[-1].strip()] = (float(select_lines[i + 2].split(" - ")[-1].strip()), float(select_lines[i + 10].split(" - ")[-1].strip()))
#                i += 11
#            tmp['candidates'] = rec
#        #if selected_lines[i + 7].split("-")[-1].strip() == 'False' and add_lines[j + 7].split("-")[-1].strip() == 'True':
#        selected = select_lines[i + 1].split("-")[-1].strip()
#        
#        while 'selected_logical_form:' not in add_lines[j]:
#            j += 1
#        selected_add = add_lines[j + 1].split("-")[-1].strip()
#       
#        if select_lines[i + 7].split("-")[-1].strip() == 'False' and tmp['candidates'][selected][1] == 1.0 and add_lines[j + 7].split("-")[-1].strip() == 'True':
#            item_id += 1
#            print('*' * 50)
#            #print(tmp)
#            for k,v in tmp.items():
#                if k == "table":
#                    print(k + ":")
#                    for vv in v.split("],"):
#                        print(vv + "],")
#                else:    
#                    print(k + ":")
#                    print(v)
#            print("selected lgf (switch):")
#            print(selected)
#            print('raw_score')
#            print(tmp['candidates'][selected][0])
#            print('align_score')
#            print(tmp['candidates'][selected][1])
#            i += 2
#            j += 2
#            print('execute log (switch):')
#            while 'wikitables_variable_free_executor' in select_lines[i]:
#                print(select_lines[i].split("-")[-1].strip())
#                i += 1
#            
#            print('##reference##')
#            print('selected lgf (add):')
#            print(selected_add)
#            print('candidate score')
#            print(tmp['candidates'][selected_add])
#            #print('execute log (add):')
#            while 'wikitables_variable_free_executor' in add_lines[j]:
#                #print(add_lines[j].split("-")[-1].strip())
#                j += 1
#        
#        while i < len(select_lines) and '*decoding:*' not in select_lines[i]:
#            i += 1
#
#        while j < len(add_lines) and '*decoding:*' not in add_lines[j]:
#            j += 1
#
