#import codecs
#from collections import defaultdict
#f = codecs.open("log_1216.txt")
#lines = f.readlines()
#errors = defaultdict(int)
#for idx in range(len(lines)):
#    if "WARNING" in lines[idx]:
#        error = lines[idx].split("-")[-1].strip().split(":")[0]
#        lgf = lines[idx - 1].split("-")[-1].strip()
#        print(lgf)
#        print(error)
#        errors[error] += 1
#for k, v in errors.items():
#    print(k)
#    print(v)
