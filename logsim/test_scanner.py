from scanner import *
from names import *
names=Names()
scanner=Scanner(r'C:\Users\david\Documents\GitHub\GF2\logsim\example1.txt',names)
for i in range(10):
    a=scanner.get_symbol()
    print(a.type)
    print(a.id)
