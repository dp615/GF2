from scanner import *
from names import *

def test_scanner():
    names=Names()
    scanner=Scanner(r'scanner_test_file.txt',names)
    types=[1,6,0,6,5,3,5,2,6,6,3,6,4,7]
    ids=[]
    a=Symbol()
    counter=0
    while a.type!=7:
        a=scanner.get_symbol()
        assert a.type==types[counter]
        counter+=1




'''
self.COMMA, self.SEMICOLON, self.EQUALS,self.DASH
        self.KEYWORD, self.NUMBER, self.NAME, self.EOF
        '''
