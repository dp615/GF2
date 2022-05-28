from scanner import *
from names import *

def test_scanner():
    names=Names()
    scanner=Scanner(r'scanner_test_file.txt',names)
    types=[1,6,0,6,5,3,5,2,6,6,3,6,4,7,8]
    ids=[None,5,None,6,1,None,2,None,7,8,None,7,0,None,None]
    a=Symbol()
    counter=0
    while a.type!=7:
        a=scanner.get_symbol()
        assert a.type==types[counter]
        assert a.id==ids[counter]
        counter+=1


