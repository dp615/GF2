from scanner import *
from names import *
names=Names()
scanner=Scanner(r'C:\Users\david\Documents\GitHub\GF2\logsim\example1.txt',names)
print(scanner.get_symbol().type)